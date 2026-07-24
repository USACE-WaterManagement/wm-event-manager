import { useEffect, useMemo, useState } from "react";
import {
  Button,
  Dropdown,
  Field,
  Fieldset,
  H3,
  Label,
  Text,
  Textarea,
} from "@usace/groundwork";
import toast from "react-hot-toast";
import type { Script } from "../scripts-manager/types";
import {
  useCreateScriptNotificationRule,
  useDeleteScriptNotificationRule,
  useCdaUserLists,
  useNotificationTemplates,
  usePreviewNotificationTemplate,
  useScriptNotificationRules,
  useUpdateScriptNotificationRule,
} from "./api";
import { JinjaTemplateField } from "./JinjaTemplateField";

interface ScriptNotificationEditorProps {
  script: Script;
}

const FieldRow = ({ children }: React.PropsWithChildren) => (
  <Field className="grid grid-cols-[120px_1fr] gap-4">{children}</Field>
);

const jobFailureData = (script: Script) => ({
  jobId: "preview-job-id",
  scriptId: script.id,
  scriptName: script.name,
  scriptSlug: script.slug,
  repoPath: script.repoPath,
  executionType: script.executionType,
  username: "preview.user",
  office: script.office,
  externalJobId: "preview-external-id",
  errorMessage: "Example failure message",
  logs: "Example job log output",
});

export const ScriptNotificationEditor = ({
  script,
}: ScriptNotificationEditorProps) => {
  const templates = useNotificationTemplates(script.office);
  const userLists = useCdaUserLists(script.office);
  const rules = useScriptNotificationRules(script.id);
  const createRule = useCreateScriptNotificationRule(script.id);
  const updateRule = useUpdateScriptNotificationRule(script.id);
  const deleteRule = useDeleteScriptNotificationRule(script.id);
  const preview = usePreviewNotificationTemplate();

  const rule = useMemo(
    () => rules.data?.find((item) => item.eventType === "job_failed"),
    [rules.data],
  );
  const activeTemplates = useMemo(
    () => templates.data?.filter((template) => template.active) ?? [],
    [templates.data],
  );
  const defaultTemplateId = activeTemplates[0]?.id ?? "";
  const selectedTemplate =
    activeTemplates.find((template) => template.id === rule?.templateId) ??
    activeTemplates[0];

  const [templateId, setTemplateId] = useState("");
  const [cdaUserListId, setCdaUserListId] = useState("");
  const [manualRecipients, setManualRecipients] = useState("");
  const [subjectTemplate, setSubjectTemplate] = useState("");
  const [bodyTemplate, setBodyTemplate] = useState("");

  useEffect(() => {
    setTemplateId(rule?.templateId ?? defaultTemplateId);
    setCdaUserListId(rule?.cdaUserListId ?? "");
    setManualRecipients(rule?.manualRecipients?.join("\n") ?? "");
    setSubjectTemplate(
      rule?.subjectTemplate ?? selectedTemplate?.subjectTemplate ?? "",
    );
    setBodyTemplate(rule?.bodyTemplate ?? selectedTemplate?.bodyTemplate ?? "");
  }, [rule, selectedTemplate, defaultTemplateId]);

  const recipientEmails = manualRecipients
    .split(/[\n,;]/)
    .map((email) => email.trim())
    .filter(Boolean);

  const payload = (active: boolean) => ({
    scriptId: script.id,
    eventType: "job_failed" as const,
    templateId,
    cdaUserListId: cdaUserListId || null,
    manualRecipients: recipientEmails,
    subjectTemplate:
      subjectTemplate === selectedTemplate?.subjectTemplate
        ? null
        : subjectTemplate,
    bodyTemplate:
      bodyTemplate === selectedTemplate?.bodyTemplate ? null : bodyTemplate,
    active,
  });

  const save = async (active = rule?.active ?? true) => {
    if (!templateId || (!cdaUserListId && recipientEmails.length === 0)) return;
    if (rule) {
      await updateRule.mutateAsync({ ruleId: rule.id, payload: payload(active) });
      toast.success(active ? "Notification saved" : "Notification disabled");
    } else {
      await createRule.mutateAsync(payload(active));
      toast.success("Notification created");
    }
  };

  const renderPreview = async () => {
    if (!templateId) return;
    await preview.mutateAsync({
      templateId,
      data: jobFailureData(script),
      subjectTemplate,
      bodyTemplate,
    });
  };

  const error =
    templates.error ||
    userLists.error ||
    rules.error ||
    createRule.error ||
    updateRule.error ||
    deleteRule.error ||
    preview.error;

  return (
    <div className="flex flex-col gap-4">
      <H3>Failed-Job Notification</H3>
      <Text>{script.name}</Text>
      {error && <Text className="text-red-500">{error.message}</Text>}
      <Fieldset className="flex flex-col gap-4">
        {activeTemplates.length > 0 ? (
          <Dropdown
            key={`template-${templateId}-${activeTemplates.length}`}
            label="Template"
            value={templateId}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
              const nextTemplate = activeTemplates.find(
                (template) => template.id === e.target.value,
              );
              setTemplateId(e.target.value);
              setSubjectTemplate(nextTemplate?.subjectTemplate ?? "");
              setBodyTemplate(nextTemplate?.bodyTemplate ?? "");
            }}
            options={activeTemplates.map((template) => (
              <option key={template.id} value={template.id}>
                {template.office ? `${template.office}: ` : "Default: "}
                {template.slug}
              </option>
            ))}
          />
        ) : (
          <Text>Create a notification template before enabling this script.</Text>
        )}
        {(userLists.data?.length ?? 0) > 0 ? (
          <Dropdown
            key={`cda-list-${cdaUserListId}-${userLists.data?.length}`}
            label="CDA user list"
            value={cdaUserListId}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
              setCdaUserListId(e.target.value)
            }
            options={[
              <option key="none" value="">
                No CDA user list
              </option>,
              ...(userLists.data ?? []).map((list) => (
              <option key={list["user-list-id"]} value={list["user-list-id"]}>
                {list["user-list-id"]}
              </option>
              )),
            ]}
          />
        ) : (
          <Text>
            No CDA user lists exist for {script.office}.{" "}
            <a
              className="underline"
              href={`${import.meta.env.VITE_CDA_UI_ROOT}/user-lists`}
              target="_blank"
              rel="noreferrer"
            >
              Create one in CDA
            </a>
            , or enter manual recipients below.
          </Text>
        )}
        <FieldRow>
          <Label htmlFor="script-notification-recipients">
            Manual recipients
          </Label>
          <Textarea
            id="script-notification-recipients"
            value={manualRecipients}
            placeholder="one@example.mil, two@example.mil"
            onChange={(event: React.ChangeEvent<HTMLTextAreaElement>) =>
              setManualRecipients(event.target.value)
            }
          />
        </FieldRow>
        <FieldRow>
          <Label htmlFor="script-notification-subject">Subject</Label>
          <JinjaTemplateField
            id="script-notification-subject"
            value={subjectTemplate}
            className="h-20"
            onChange={setSubjectTemplate}
          />
        </FieldRow>
        <FieldRow>
          <Label htmlFor="script-notification-body">Body</Label>
          <JinjaTemplateField
            id="script-notification-body"
            value={bodyTemplate}
            onChange={setBodyTemplate}
          />
        </FieldRow>
      </Fieldset>
      <div className="flex flex-wrap gap-3">
        <Button
          type="button"
          disabled={
            !templateId ||
            (!cdaUserListId && recipientEmails.length === 0) ||
            createRule.isPending ||
            updateRule.isPending
          }
          onClick={() => save(true)}
        >
          {rule ? "Save" : "Create"}
        </Button>
        {rule && (
          <Button
            type="button"
            disabled={updateRule.isPending}
            onClick={() => save(!rule.active)}
          >
            {rule.active ? "Disable" : "Enable"}
          </Button>
        )}
        {rule && (
          <Button
            type="button"
            disabled={deleteRule.isPending}
            onClick={async () => {
              await deleteRule.mutateAsync(rule.id);
              toast.success("Notification deleted");
            }}
          >
            Delete
          </Button>
        )}
        <Button type="button" disabled={!templateId} onClick={renderPreview}>
          Preview
        </Button>
      </div>
      {preview.data && (
        <div className="grid gap-2 border-t border-gray-300 pt-4">
          <Text>{preview.data.subject}</Text>
          <Textarea readOnly value={preview.data.body} className="h-32" />
        </div>
      )}
    </div>
  );
};
