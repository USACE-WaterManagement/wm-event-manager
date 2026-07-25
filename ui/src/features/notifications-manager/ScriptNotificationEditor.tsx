import { useEffect, useMemo, useState } from "react";
import {
  Badge,
  Button,
  Card,
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
  <Field className="grid grid-cols-1 gap-2 sm:grid-cols-[140px_minmax(0,1fr)] sm:gap-4">
    {children}
  </Field>
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
  const selectedTemplate =
    activeTemplates.find((template) => template.id === rule?.templateId) ??
    activeTemplates[0];
  const selectedTemplateId = selectedTemplate?.id ?? "";

  const [templateId, setTemplateId] = useState("");
  const [cdaUserListIdOverride, setCdaUserListIdOverride] = useState<
    string | undefined
  >();
  const [manualRecipients, setManualRecipients] = useState("");
  const [subjectTemplate, setSubjectTemplate] = useState("");
  const [bodyTemplate, setBodyTemplate] = useState("");
  const cdaUserListId =
    cdaUserListIdOverride ?? rule?.cdaUserListId ?? "";

  useEffect(() => {
    setTemplateId(selectedTemplateId);
    setManualRecipients(rule?.manualRecipients?.join("\n") ?? "");
    setSubjectTemplate(
      rule?.subjectTemplate ?? selectedTemplate?.subjectTemplate ?? "",
    );
    setBodyTemplate(rule?.bodyTemplate ?? selectedTemplate?.bodyTemplate ?? "");
  }, [rule, selectedTemplate, selectedTemplateId]);

  useEffect(() => {
    setCdaUserListIdOverride(undefined);
  }, [script.id, rule?.id]);

  const recipientEmails = manualRecipients
    .split(/[\n,;]/)
    .map((email) => email.trim())
    .filter(Boolean);
  const invalidRecipients = recipientEmails.filter(
    (email) => !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email),
  );
  const initialValues = {
    templateId: selectedTemplateId,
    cdaUserListId: rule?.cdaUserListId ?? "",
    manualRecipients: rule?.manualRecipients?.join("\n") ?? "",
    subjectTemplate: rule?.subjectTemplate ?? selectedTemplate?.subjectTemplate ?? "",
    bodyTemplate: rule?.bodyTemplate ?? selectedTemplate?.bodyTemplate ?? "",
  };
  const dirty =
    JSON.stringify({
      templateId,
      cdaUserListId,
      manualRecipients,
      subjectTemplate,
      bodyTemplate,
    }) !== JSON.stringify(initialValues);

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
    if (
      !templateId ||
      invalidRecipients.length > 0 ||
      (!cdaUserListId && recipientEmails.length === 0)
    )
      return;
    if (rule) {
      await updateRule.mutateAsync({ ruleId: rule.id, payload: payload(active) });
      setCdaUserListIdOverride(undefined);
      toast.success(active ? "Notification saved" : "Notification disabled");
    } else {
      await createRule.mutateAsync(payload(active));
      setCdaUserListIdOverride(undefined);
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
    <Card className="flex min-w-0 flex-col gap-5 p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <H3>Failed-job email</H3>
          <Text>{script.name}</Text>
        </div>
        <Badge color={rule?.active ? "green" : "zinc"}>
          {rule?.active ? "Enabled" : "Not enabled"}
        </Badge>
      </div>
      {error && (
        <div
          role="alert"
          className="rounded-lg border border-red-200 bg-red-50 p-3 text-red-800"
        >
          {error.message}
        </div>
      )}
      <Fieldset className="flex flex-col gap-4">
        {activeTemplates.length > 0 ? (
          <Dropdown
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
                {template.slug}
              </option>
            ))}
          />
        ) : (
          <Text>Create a notification template before enabling this script.</Text>
        )}
        {userLists.isLoading ? (
          <Text role="status">Loading CDA user lists…</Text>
        ) : (userLists.data?.length ?? 0) > 0 ? (
          <Dropdown
            key={`cda-list-${cdaUserListId}-${userLists.data?.length}`}
            label="CDA user list"
            defaultValue={cdaUserListId}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
              setCdaUserListIdOverride(e.target.value)
            }
            options={[
              <option key="none" value="">
                No CDA user list
              </option>,
              ...(userLists.data ?? []).map((list) => (
                <option key={list["user-list-id"]} value={list["user-list-id"]}>
                  {list["user-list-id"]}
                  {list.description ? ` — ${list.description}` : ""}
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
        <Text>
          <a
            className="font-medium text-blue-700 underline"
            href={`${import.meta.env.VITE_CDA_UI_ROOT}/user-lists`}
            target="_blank"
            rel="noreferrer"
          >
            Manage user lists in CDA
          </a>
        </Text>
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
          {recipientEmails.length > 0 && (
            <div className="col-start-1 flex flex-wrap gap-2 sm:col-start-2">
              {recipientEmails.map((email) => (
                <Badge
                  key={email}
                  color={invalidRecipients.includes(email) ? "red" : "blue"}
                >
                  {email}
                </Badge>
              ))}
            </div>
          )}
          {invalidRecipients.length > 0 && (
            <Text className="col-start-1 text-red-700 sm:col-start-2" role="alert">
              Correct the highlighted email addresses before saving.
            </Text>
          )}
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
            !dirty ||
            invalidRecipients.length > 0 ||
            (!cdaUserListId && recipientEmails.length === 0) ||
            createRule.isPending ||
            updateRule.isPending
          }
          onClick={() => save(true)}
        >
          {rule ? "Save changes" : "Enable notification"}
        </Button>
        {rule && (
          <Button
            type="button"
            disabled={updateRule.isPending || invalidRecipients.length > 0}
            onClick={() => save(!rule.active)}
          >
            {rule.active ? "Disable notification" : "Enable notification"}
          </Button>
        )}
        {rule && (
          <Button
            type="button"
            disabled={deleteRule.isPending}
            color="danger"
            style="outline"
            onClick={async () => {
              if (!window.confirm("Delete this failed-job notification?")) return;
              await deleteRule.mutateAsync(rule.id);
              toast.success("Notification deleted");
            }}
          >
            Delete notification
          </Button>
        )}
        <Button
          type="button"
          disabled={!templateId || preview.isPending}
          onClick={renderPreview}
        >
          Preview email
        </Button>
      </div>
      {preview.data && (
        <section className="grid gap-3 rounded-lg border border-zinc-200 bg-white p-4">
          <Badge color="blue">Email preview</Badge>
          <H3 className="text-lg">{preview.data.subject}</H3>
          <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded-lg bg-zinc-50 p-4 font-sans text-sm">
            {preview.data.body}
          </pre>
        </section>
      )}
      {dirty && <Text role="status">You have unsaved notification changes.</Text>}
    </Card>
  );
};
