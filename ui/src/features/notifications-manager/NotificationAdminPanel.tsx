import { useMemo, useState } from "react";
import {
  Button,
  Dropdown,
  Field,
  Fieldset,
  H3,
  Input,
  Label,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  Text,
  Textarea,
} from "@usace/groundwork";
import type { Script } from "../scripts-manager/types";
import {
  useCreateNotificationGroup,
  useCreateNotificationGroupMember,
  useCreateNotificationTemplate,
  useCreateScriptNotificationRule,
  useDeleteScriptNotificationRule,
  useNotificationGroupMembers,
  useNotificationGroups,
  useNotificationTemplates,
  usePreviewNotificationTemplate,
  useScriptNotificationRules,
} from "./api";

const slugify = (str: string) =>
  str
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/[\s_-]+/g, "-")
    .replace(/^-+|-+$/g, "");

const FieldRow = ({ children }: React.PropsWithChildren) => (
  <Field className="grid grid-cols-[120px_1fr] gap-4">{children}</Field>
);

interface NotificationAdminPanelProps {
  office: string;
  selectedScript?: Script;
}

export const NotificationAdminPanel = ({
  office,
  selectedScript,
}: NotificationAdminPanelProps) => {
  const templates = useNotificationTemplates(office);
  const groups = useNotificationGroups(office);
  const rules = useScriptNotificationRules(selectedScript?.id);
  const createTemplate = useCreateNotificationTemplate(office);
  const createGroup = useCreateNotificationGroup(office);
  const createRule = useCreateScriptNotificationRule(selectedScript?.id);
  const deleteRule = useDeleteScriptNotificationRule(selectedScript?.id);
  const preview = usePreviewNotificationTemplate();

  const [templateForm, setTemplateForm] = useState({
    slug: "job_failure_v1",
    subjectTemplate: "Batch job {{ scriptName }} failed",
    bodyTemplate:
      "Job {{ jobId }} failed for {{ office }}.\nError: {{ errorMessage }}\nLogs: {{ logs }}",
  });
  const [groupForm, setGroupForm] = useState({
    name: "Data Admins",
    slug: "data-admins",
  });
  const [memberEmail, setMemberEmail] = useState("batch-alerts-local@example.mil");
  const [selectedTemplateId, setSelectedTemplateId] = useState("");
  const [selectedGroupId, setSelectedGroupId] = useState("");

  const activeTemplates = useMemo(
    () => templates.data?.filter((template) => template.active) ?? [],
    [templates.data],
  );
  const activeGroups = useMemo(
    () => groups.data?.filter((group) => group.active) ?? [],
    [groups.data],
  );
  const selectedGroupForMembers = selectedGroupId || activeGroups[0]?.id;
  const createMember = useCreateNotificationGroupMember(selectedGroupForMembers);
  const members = useNotificationGroupMembers(selectedGroupForMembers);
  const activeRules = rules.data?.filter((rule) => rule.active) ?? [];

  const isLoading = templates.isLoading || groups.isLoading || rules.isLoading;
  const error =
    templates.error ||
    groups.error ||
    rules.error ||
    createTemplate.error ||
    createGroup.error ||
    createMember.error ||
    createRule.error ||
    deleteRule.error ||
    preview.error;

  const createTemplateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await createTemplate.mutateAsync({
      office,
      slug: templateForm.slug || slugify(templateForm.subjectTemplate),
      subjectTemplate: templateForm.subjectTemplate,
      bodyTemplate: templateForm.bodyTemplate,
      active: true,
    });
  };

  const createGroupSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const group = await createGroup.mutateAsync({
      office,
      slug: groupForm.slug || slugify(groupForm.name),
      name: groupForm.name,
      active: true,
    });
    setSelectedGroupId(group.id);
  };

  const createMemberSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedGroupForMembers) return;
    await createMember.mutateAsync({ email: memberEmail, active: true });
    setMemberEmail("");
  };

  const createRuleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedScript) return;
    await createRule.mutateAsync({
      scriptId: selectedScript.id,
      eventType: "job_failed",
      templateId: selectedTemplateId || activeTemplates[0]?.id,
      groupId: selectedGroupId || activeGroups[0]?.id,
      active: true,
    });
  };

  const previewTemplate = async () => {
    const templateId = selectedTemplateId || activeTemplates[0]?.id;
    if (!templateId) return;
    await preview.mutateAsync({
      templateId,
      data: {
        jobId: "preview-job-id",
        scriptName: selectedScript?.name ?? "Example Script",
        office,
        errorMessage: "Example failure message",
        logs: "Example job log output",
      },
    });
  };

  return (
    <section className="mt-6 p-4 rounded-lg bg-gray-200">
      <div className="flex flex-col gap-6">
        <header className="flex items-center justify-between">
          <H3>{office.toUpperCase()} Failed-Job Notifications</H3>
          <Button
            type="button"
            onClick={previewTemplate}
            disabled={activeTemplates.length < 1 || preview.isPending}
          >
            Preview
          </Button>
        </header>

        {isLoading && <Text>Loading notification configuration...</Text>}
        {error && <Text className="text-red-500">{error.message}</Text>}

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
          <form onSubmit={createTemplateSubmit} className="flex flex-col gap-3">
            <H3>Templates</H3>
            <Fieldset
              disabled={createTemplate.isPending}
              className="flex flex-col gap-2"
            >
              <FieldRow>
                <Label htmlFor="template-slug">Slug</Label>
                <Input
                  id="template-slug"
                  value={templateForm.slug}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    setTemplateForm((prev) => ({ ...prev, slug: e.target.value }))
                  }
                />
              </FieldRow>
              <FieldRow>
                <Label htmlFor="template-subject">Subject</Label>
                <Input
                  id="template-subject"
                  value={templateForm.subjectTemplate}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    setTemplateForm((prev) => ({
                      ...prev,
                      subjectTemplate: e.target.value,
                    }))
                  }
                />
              </FieldRow>
              <FieldRow>
                <Label htmlFor="template-body">Body</Label>
                <Textarea
                  id="template-body"
                  value={templateForm.bodyTemplate}
                  className="h-32"
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                    setTemplateForm((prev) => ({
                      ...prev,
                      bodyTemplate: e.target.value,
                    }))
                  }
                />
              </FieldRow>
              <Button type="submit">Create</Button>
            </Fieldset>
            <Table>
              <TableHead>
                <TableRow>
                  <TableHeader>Slug</TableHeader>
                  <TableHeader>Active</TableHeader>
                </TableRow>
              </TableHead>
              <TableBody>
                {templates.data?.map((template) => (
                  <TableRow key={template.id}>
                    <TableCell>{template.slug}</TableCell>
                    <TableCell>{template.active ? "true" : "false"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </form>

          <div className="flex flex-col gap-3">
            <H3>Groups</H3>
            <form onSubmit={createGroupSubmit}>
              <Fieldset
                disabled={createGroup.isPending}
                className="flex flex-col gap-2"
              >
                <FieldRow>
                  <Label htmlFor="group-name">Name</Label>
                  <Input
                    id="group-name"
                    value={groupForm.name}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                      setGroupForm((prev) => ({
                        ...prev,
                        name: e.target.value,
                        slug: slugify(e.target.value),
                      }))
                    }
                  />
                </FieldRow>
                <FieldRow>
                  <Label htmlFor="group-slug">Slug</Label>
                  <Input
                    id="group-slug"
                    value={groupForm.slug}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                      setGroupForm((prev) => ({ ...prev, slug: e.target.value }))
                    }
                  />
                </FieldRow>
                <Button type="submit">Create</Button>
              </Fieldset>
            </form>
            <Dropdown
              label="Member Group"
              value={selectedGroupForMembers ?? ""}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                setSelectedGroupId(e.target.value)
              }
              options={activeGroups.map((group) => (
                <option key={group.id} value={group.id}>
                  {group.name}
                </option>
              ))}
            />
            <form onSubmit={createMemberSubmit} className="flex gap-2">
              <Input
                aria-label="Member email"
                value={memberEmail}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setMemberEmail(e.target.value)
                }
              />
              <Button
                type="submit"
                disabled={!selectedGroupForMembers || createMember.isPending}
              >
                Add
              </Button>
            </form>
            <ul className="list-disc pl-6">
              {members.data?.map((member) => (
                <li key={member.id}>{member.email}</li>
              ))}
            </ul>
          </div>

          <form onSubmit={createRuleSubmit} className="flex flex-col gap-3">
            <H3>Selected Script Rule</H3>
            {!selectedScript && <Text>Select a script to configure a rule.</Text>}
            {selectedScript && (
              <>
                <Text>{selectedScript.name}</Text>
                <Dropdown
                  label="Template"
                  value={selectedTemplateId || activeTemplates[0]?.id || ""}
                  onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                    setSelectedTemplateId(e.target.value)
                  }
                  options={activeTemplates.map((template) => (
                    <option key={template.id} value={template.id}>
                      {template.slug}
                    </option>
                  ))}
                />
                <Dropdown
                  label="Group"
                  value={selectedGroupId || activeGroups[0]?.id || ""}
                  onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                    setSelectedGroupId(e.target.value)
                  }
                  options={activeGroups.map((group) => (
                    <option key={group.id} value={group.id}>
                      {group.name}
                    </option>
                  ))}
                />
                <Button
                  type="submit"
                  disabled={
                    !selectedScript ||
                    activeTemplates.length < 1 ||
                    activeGroups.length < 1 ||
                    createRule.isPending
                  }
                >
                  Enable Failed Alert
                </Button>
                {activeRules.length > 0 && (
                  <div className="flex flex-col gap-2">
                    {activeRules.map((rule) => (
                      <div
                        key={rule.id}
                        className="flex items-center justify-between gap-4"
                      >
                        <Text>Failed-job alert is enabled.</Text>
                        <Button
                          type="button"
                          onClick={() => deleteRule.mutate(rule.id)}
                        >
                          Disable
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </form>
        </div>

        {preview.data && (
          <div className="grid grid-cols-[120px_1fr] gap-4 border-t border-gray-300 pt-4">
            <Text>Subject</Text>
            <Text>{preview.data.subject}</Text>
            <Text>Body</Text>
            <Textarea readOnly value={preview.data.body} className="h-32" />
          </div>
        )}
      </div>
    </section>
  );
};
