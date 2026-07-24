import { useMemo, useState } from "react";
import {
  Button,
  Field,
  Fieldset,
  H2,
  H3,
  Input,
  Label,
  Sidebar,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  Text,
} from "@usace/groundwork";
import { useAuth } from "@usace-watermanagement/groundwork-water";
import toast from "react-hot-toast";
import { FaCopy, FaPlus, FaTrash } from "react-icons/fa6";
import {
  useCreateNotificationGroup,
  useCreateNotificationGroupMember,
  useCreateNotificationTemplate,
  useDeleteNotificationGroup,
  useDeleteNotificationGroupMember,
  useDeleteNotificationTemplate,
  useNotificationGroupMembers,
  useNotificationGroups,
  useNotificationTemplates,
  useUpdateNotificationGroup,
  useUpdateNotificationTemplate,
} from "./api";
import { JinjaTemplateField } from "./JinjaTemplateField";
import type { NotificationGroup, NotificationTemplate } from "./types";

const slugify = (str: string) =>
  str
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/[\s_-]+/g, "-")
    .replace(/^-+|-+$/g, "");

const emptyTemplate = () => ({
  id: "",
  office: "",
  slug: "job_failure_v1",
  subjectTemplate: "Batch job {{ scriptName }} failed",
  bodyTemplate:
    "Job {{ jobId }} failed for {{ office }}.\nError: {{ errorMessage }}\nLogs: {{ logs }}",
  active: true,
});

const emptyGroup = () => ({
  id: "",
  slug: "",
  name: "",
  active: true,
});

const FieldRow = ({ children }: React.PropsWithChildren) => (
  <Field className="grid grid-cols-[120px_1fr] gap-4">{children}</Field>
);

const setupSidebarLinks = [
  { id: "setup-groups", text: "Groups", href: "" },
  {
    id: "setup-notifications",
    text: "Notifications",
    href: "",
  },
];

export const NotificationsManager = () => {
  const auth = useAuth();
  const [pane, setPane] = useState<"groups" | "templates">("groups");

  const templates = useNotificationTemplates();
  const groups = useNotificationGroups();
  const createTemplate = useCreateNotificationTemplate();
  const updateTemplate = useUpdateNotificationTemplate();
  const deleteTemplate = useDeleteNotificationTemplate();
  const createGroup = useCreateNotificationGroup();
  const updateGroup = useUpdateNotificationGroup();
  const deleteGroup = useDeleteNotificationGroup();

  const [selectedTemplateId, setSelectedTemplateId] = useState("");
  const [selectedGroupId, setSelectedGroupId] = useState("");
  const [templateForm, setTemplateForm] = useState(emptyTemplate);
  const [groupForm, setGroupForm] = useState(emptyGroup);
  const [memberEmail, setMemberEmail] = useState("");

  const selectedTemplate = templates.data?.find(
    (template) => template.id === selectedTemplateId,
  );
  const selectedGroup = groups.data?.find((group) => group.id === selectedGroupId);
  const groupMembers = useNotificationGroupMembers(selectedGroupId);
  const createMember = useCreateNotificationGroupMember(selectedGroupId);
  const deleteMember = useDeleteNotificationGroupMember(selectedGroupId);

  const sortedTemplates = useMemo(
    () => [...(templates.data ?? [])].sort((a, b) => a.slug.localeCompare(b.slug)),
    [templates.data],
  );
  const sortedGroups = useMemo(
    () => [...(groups.data ?? [])].sort((a, b) => a.name.localeCompare(b.name)),
    [groups.data],
  );

  if (!auth.isAuth) return <span>Login required to edit notifications.</span>;

  const selectTemplate = (template: NotificationTemplate) => {
    setSelectedTemplateId(template.id);
    setTemplateForm({
      id: template.id,
      office: template.office ?? "",
      slug: template.slug,
      subjectTemplate: template.subjectTemplate,
      bodyTemplate: template.bodyTemplate,
      active: template.active,
    });
  };

  const selectGroup = (group: NotificationGroup) => {
    setSelectedGroupId(group.id);
    setGroupForm({
      id: group.id,
      slug: group.slug,
      name: group.name,
      active: group.active,
    });
  };

  const startNewGroup = () => {
    setSelectedGroupId("");
    setGroupForm({ ...emptyGroup(), name: "New Group", slug: "new-group" });
  };

  const copySelectedGroup = () => {
    if (!selectedGroup) return;
    setSelectedGroupId("");
    setGroupForm({
      id: "",
      name: `${selectedGroup.name} Copy`,
      slug: `${selectedGroup.slug}-copy`,
      active: true,
    });
  };

  const saveTemplate = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      office: templateForm.office || null,
      slug: templateForm.slug || slugify(templateForm.subjectTemplate),
      subjectTemplate: templateForm.subjectTemplate,
      bodyTemplate: templateForm.bodyTemplate,
      active: templateForm.active,
    };
    if (templateForm.id) {
      const template = await updateTemplate.mutateAsync({
        templateId: templateForm.id,
        payload,
      });
      selectTemplate(template);
      toast.success("Template updated");
    } else {
      const template = await createTemplate.mutateAsync(payload);
      selectTemplate(template);
      toast.success("Template created");
    }
  };

  const saveGroup = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      office: null,
      slug: groupForm.slug || slugify(groupForm.name),
      name: groupForm.name,
      active: groupForm.active,
    };
    if (groupForm.id) {
      const group = await updateGroup.mutateAsync({ groupId: groupForm.id, payload });
      selectGroup(group);
      toast.success("Group updated");
    } else {
      const group = await createGroup.mutateAsync(payload);
      if (selectedGroup && groupMembers.data) {
        await Promise.all(
          groupMembers.data.map((member) =>
            createMember.mutateAsync({
              groupId: group.id,
              email: member.email,
              active: member.active,
            }),
          ),
        );
      }
      selectGroup(group);
      toast.success("Group created");
    }
  };

  const addMember = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedGroupId || !memberEmail) return;
    await createMember.mutateAsync({ email: memberEmail, active: true });
    setMemberEmail("");
    toast.success("Member added");
  };

  const removeGroup = async () => {
    if (!selectedGroup) return;
    await deleteGroup.mutateAsync(selectedGroup.id);
    setSelectedGroupId("");
    setGroupForm(emptyGroup());
    toast.success("Group deleted");
  };

  const removeTemplate = async () => {
    if (!selectedTemplate) return;
    await deleteTemplate.mutateAsync(selectedTemplate.id);
    setSelectedTemplateId("");
    setTemplateForm(emptyTemplate());
    toast.success("Notification template deleted");
  };

  return (
    <div className="flex flex-col gap-6">
      <H2>Setup</H2>
      <div className="grid grid-cols-1 gap-6 md:grid-cols-[220px_320px_1fr]">
        <aside
          onClickCapture={(event) => {
            const target = event.target as HTMLElement;
            const anchor = target.closest("a");
            const text = anchor?.textContent?.trim();
            if (text !== "Groups" && text !== "Notifications") return;
            event.preventDefault();
            event.stopPropagation();
            setPane(text === "Groups" ? "groups" : "templates");
          }}
        >
          <Sidebar
            title="Setup"
            selectedPath=""
            sidebarLinks={setupSidebarLinks}
          />
        </aside>

        {pane === "groups" ? (
          <>
            <section className="flex flex-col gap-3">
              <div className="flex items-center justify-between border-b border-gray-300 pb-2">
                <H3>Groups</H3>
                <div className="flex gap-2">
                  <button
                    type="button"
                    title="Add group"
                    aria-label="Add group"
                    onClick={startNewGroup}
                  >
                    <FaPlus />
                  </button>
                  <button
                    type="button"
                    title="Copy selected group"
                    aria-label="Copy selected group"
                    disabled={!selectedGroup}
                    onClick={copySelectedGroup}
                  >
                    <FaCopy />
                  </button>
                </div>
              </div>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableHeader>Name</TableHeader>
                    <TableHeader>Slug</TableHeader>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {sortedGroups.map((group) => (
                    <TableRow
                      key={group.id}
                      className={
                        group.id === selectedGroupId
                          ? "cursor-pointer bg-blue-100"
                          : "cursor-pointer hover:bg-gray-100"
                      }
                      onClick={() => selectGroup(group)}
                    >
                      <TableCell>{group.name}</TableCell>
                      <TableCell>{group.slug}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </section>

            <section className="flex flex-col gap-4 rounded-lg bg-gray-100 p-4">
              <div className="flex items-center justify-between">
                <H3>{groupForm.id ? "Edit Group" : "New Group"}</H3>
                {selectedGroup && (
                  <button
                    type="button"
                    title="Delete group"
                    aria-label="Delete group"
                    onClick={removeGroup}
                  >
                    <FaTrash className="text-red-600" />
                  </button>
                )}
              </div>
              <form onSubmit={saveGroup}>
                <Fieldset className="flex flex-col gap-3">
                  <FieldRow>
                    <Label htmlFor="group-name">Name</Label>
                    <Input
                      id="group-name"
                      value={groupForm.name}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                        setGroupForm((prev) => ({
                          ...prev,
                          name: e.target.value,
                          slug: prev.slug || slugify(e.target.value),
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
                  <Button type="submit">{groupForm.id ? "Update" : "Create"}</Button>
                </Fieldset>
              </form>
              {selectedGroup ? (
                <form onSubmit={addMember} className="flex flex-col gap-3">
                  <Text>Members</Text>
                  <div className="flex gap-2">
                    <Input
                      aria-label="Member email"
                      value={memberEmail}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                        setMemberEmail(e.target.value)
                      }
                    />
                    <Button type="submit" disabled={!memberEmail}>
                      Add
                    </Button>
                  </div>
                  <ul className="flex flex-col gap-2">
                    {groupMembers.data?.map((member) => (
                      <li
                        key={member.id}
                        className="flex items-center justify-between rounded-lg bg-white px-3 py-2"
                      >
                        <span>{member.email}</span>
                        <button
                          type="button"
                          aria-label={`Remove ${member.email}`}
                          onClick={() => deleteMember.mutate(member.id)}
                        >
                          <FaTrash className="text-red-600" />
                        </button>
                      </li>
                    ))}
                  </ul>
                </form>
              ) : (
                <Text>Create or select a group to manage members.</Text>
              )}
            </section>
          </>
        ) : (
          <>
            <section className="flex flex-col gap-3">
              <div className="flex items-center justify-between border-b border-gray-300 pb-2">
                <H3>Notifications</H3>
                <button
                  type="button"
                  title="Add template"
                  aria-label="Add template"
                  onClick={() => {
                    setSelectedTemplateId("");
                    setTemplateForm(emptyTemplate());
                  }}
                >
                  <FaPlus />
                </button>
              </div>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableHeader>Slug</TableHeader>
                    <TableHeader>Scope</TableHeader>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {sortedTemplates.map((template) => (
                    <TableRow
                      key={template.id}
                      className={
                        template.id === selectedTemplateId
                          ? "cursor-pointer bg-blue-100"
                          : "cursor-pointer hover:bg-gray-100"
                      }
                      onClick={() => selectTemplate(template)}
                    >
                      <TableCell>{template.slug}</TableCell>
                      <TableCell>{template.office ?? "Default"}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </section>

            <section className="flex flex-col gap-4 rounded-lg bg-gray-100 p-4">
              <div className="flex items-center justify-between">
                <H3>{templateForm.id ? "Edit Template" : "New Template"}</H3>
                {selectedTemplate && (
                  <button
                    type="button"
                    title="Delete template"
                    aria-label="Delete template"
                    onClick={removeTemplate}
                  >
                    <FaTrash className="text-red-600" />
                  </button>
                )}
              </div>
              <form onSubmit={saveTemplate}>
                <Fieldset className="flex flex-col gap-3">
                  <FieldRow>
                    <Label htmlFor="template-office">Office</Label>
                    <Input
                      id="template-office"
                      placeholder="Default"
                      value={templateForm.office}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                        setTemplateForm((prev) => ({
                          ...prev,
                          office: e.target.value.toUpperCase(),
                        }))
                      }
                    />
                  </FieldRow>
                  <FieldRow>
                    <Label htmlFor="template-slug">Slug</Label>
                    <Input
                      id="template-slug"
                      value={templateForm.slug}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                        setTemplateForm((prev) => ({
                          ...prev,
                          slug: e.target.value,
                        }))
                      }
                    />
                  </FieldRow>
                  <FieldRow>
                    <Label htmlFor="template-subject">Subject</Label>
                    <JinjaTemplateField
                      id="template-subject"
                      value={templateForm.subjectTemplate}
                      className="h-20"
                      onChange={(value) =>
                        setTemplateForm((prev) => ({
                          ...prev,
                          subjectTemplate: value,
                        }))
                      }
                    />
                  </FieldRow>
                  <FieldRow>
                    <Label htmlFor="template-body">Body</Label>
                    <JinjaTemplateField
                      id="template-body"
                      value={templateForm.bodyTemplate}
                      onChange={(value) =>
                        setTemplateForm((prev) => ({
                          ...prev,
                          bodyTemplate: value,
                        }))
                      }
                    />
                  </FieldRow>
                  <Button type="submit">
                    {templateForm.id ? "Update" : "Create"}
                  </Button>
                </Fieldset>
              </form>
            </section>
          </>
        )}
      </div>
    </div>
  );
};
