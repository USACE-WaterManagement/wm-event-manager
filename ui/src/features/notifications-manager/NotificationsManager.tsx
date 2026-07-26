import { useEffect, useMemo, useState } from "react";
import {
  Badge,
  Button,
  Card,
  Checkboxes,
  Description,
  Field,
  Fieldset,
  H2,
  H3,
  Input,
  Label,
  Skeleton,
  Text,
} from "@usace/groundwork";
import { useAuth } from "@usace-watermanagement/groundwork-water";
import toast from "react-hot-toast";
import { FaEnvelope, FaPlus } from "react-icons/fa6";
import { HelpTip } from "../../shared/components/HelpTip";
import { OfficeSelector } from "../../shared/components/OfficeSelector";
import { useRememberedOffice } from "../../shared/hooks/useRememberedOffice";
import useAdminOffices from "../scripts-manager/useAdminOffices";
import {
  useCreateNotificationTemplate,
  useDeleteNotificationTemplate,
  useNotificationTemplates,
  usePreviewNotificationTemplate,
  useUpdateNotificationTemplate,
} from "./api";
import { JinjaTemplateField } from "./JinjaTemplateField";
import { TemplateVariablesHelp } from "./TemplateVariablesHelp";
import type { NotificationTemplate } from "./types";

const emptyTemplate = (office: string) => ({
  id: "",
  office,
  slug: "job_failure_v1",
  subjectTemplate: "Batch job {{ scriptName }} failed",
  bodyTemplate:
    "Job {{ jobId }} failed for {{ office }}.\nError: {{ errorMessage }}\n\nReview the job and logs in Batch Events.",
  active: true,
});

const formFromTemplate = (template: NotificationTemplate) => ({
  id: template.id,
  office: template.office ?? "",
  slug: template.slug,
  subjectTemplate: template.subjectTemplate,
  bodyTemplate: template.bodyTemplate,
  active: template.active,
});

export const NotificationsManager = () => {
  const auth = useAuth();
  const adminOffices = useAdminOffices();
  const [office, setOffice] = useRememberedOffice(adminOffices.data ?? []);
  const selectedOffice = office ?? "";
  const templates = useNotificationTemplates(selectedOffice);
  const createTemplate = useCreateNotificationTemplate(selectedOffice);
  const updateTemplate = useUpdateNotificationTemplate(selectedOffice);
  const deleteTemplate = useDeleteNotificationTemplate(selectedOffice);
  const preview = usePreviewNotificationTemplate();
  const resetPreview = preview.reset;
  const [selectedTemplateId, setSelectedTemplateId] = useState("");
  const [templateForm, setTemplateForm] = useState(() => emptyTemplate(""));
  const [deleteConfirm, setDeleteConfirm] = useState(false);

  const sortedTemplates = useMemo(
    () =>
      [...(templates.data ?? [])].sort((a, b) => a.slug.localeCompare(b.slug)),
    [templates.data],
  );
  const selectedTemplate = sortedTemplates.find(
    (template) => template.id === selectedTemplateId,
  );
  const initialForm = selectedTemplate
    ? formFromTemplate(selectedTemplate)
    : emptyTemplate(selectedOffice);
  const dirty = JSON.stringify(templateForm) !== JSON.stringify(initialForm);
  const pending =
    createTemplate.isPending ||
    updateTemplate.isPending ||
    deleteTemplate.isPending ||
    preview.isPending;
  const error =
    adminOffices.error ||
    templates.error ||
    createTemplate.error ||
    updateTemplate.error ||
    deleteTemplate.error ||
    preview.error;

  useEffect(() => {
    setSelectedTemplateId("");
    setTemplateForm(emptyTemplate(selectedOffice));
    setDeleteConfirm(false);
    resetPreview();
  }, [selectedOffice, resetPreview]);

  if (!auth.isAuth) {
    return (
      <Card className="mx-auto max-w-xl p-8 text-center">
        <H2>Email templates</H2>
        <Text className="mt-2">Log in to manage notification templates.</Text>
        <Button className="mt-5" type="button" onClick={auth.login}>
          Log in
        </Button>
      </Card>
    );
  }
  if (adminOffices.isLoading) {
    return <Skeleton className="h-48 w-full" />;
  }
  if (!adminOffices.data?.length) {
    return (
      <Card className="p-6">
        <H2>Email templates</H2>
        <Text className="mt-2">
          You do not have script administrator access for any offices.
        </Text>
      </Card>
    );
  }

  const selectTemplate = (template: NotificationTemplate) => {
    setSelectedTemplateId(template.id);
    setTemplateForm(formFromTemplate(template));
    setDeleteConfirm(false);
    resetPreview();
  };

  const startNew = () => {
    if (dirty && !window.confirm("Discard unsaved template changes?")) return;
    setSelectedTemplateId("");
    setTemplateForm(emptyTemplate(selectedOffice));
    setDeleteConfirm(false);
    preview.reset();
  };

  const saveTemplate = async (event: React.FormEvent) => {
    event.preventDefault();
    const payload = {
      office: selectedOffice,
      slug: templateForm.slug.trim(),
      subjectTemplate: templateForm.subjectTemplate,
      bodyTemplate: templateForm.bodyTemplate,
      active: templateForm.active,
    };
    try {
      const saved = templateForm.id
        ? await updateTemplate.mutateAsync({
            templateId: templateForm.id,
            payload,
          })
        : await createTemplate.mutateAsync(payload);
      selectTemplate(saved);
      toast.success(templateForm.id ? "Template updated" : "Template created");
    } catch {
      // The shared request helper displays the API error.
    }
  };

  const renderPreview = async () => {
    if (!templateForm.id) return;
    try {
      await preview.mutateAsync({
        templateId: templateForm.id,
        data: {
          jobId: "preview-job-id",
          scriptId: "preview-script-id",
          scriptName: "Hourly data load",
          scriptSlug: "hourly-data-load",
          repoPath: "bin/hourly.sh",
          executionType: "shell",
          username: "preview.user",
          office: selectedOffice,
          externalJobId: "preview-external-id",
          errorMessage: "Example failure message",
          logs: "Open Batch Events to review the job log.",
          status: "Failed",
        },
        subjectTemplate: templateForm.subjectTemplate,
        bodyTemplate: templateForm.bodyTemplate,
      });
    } catch {
      // The shared request helper displays the API error.
    }
  };

  return (
    <section className="flex min-w-0 flex-col gap-6 pb-10">
      <header className="flex flex-col gap-4 border-b border-zinc-200 pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <Badge color="blue">Setup</Badge>
          <H2 className="mt-2">Email templates</H2>
          <Text className="mt-2 max-w-3xl">
            Define office-scoped messages for failed-job notifications.
            Recipient lists are created and maintained in CDA.
          </Text>
        </div>
        <Button type="button" onClick={startNew}>
          <FaPlus aria-hidden="true" />
          New template
        </Button>
      </header>

      {error && (
        <div
          role="alert"
          className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800"
        >
          {error.message}
        </div>
      )}

      <Card className="p-5">
        <Field className="max-w-sm">
          <div className="flex items-center gap-1">
            <Label>Office</Label>
            <HelpTip title="Office-scoped templates">
              A template is available only to scripts owned by this office. The
              same template ID may be used independently by another office.
            </HelpTip>
          </div>
          <Description>
            Templates can only be used by scripts in this office.
          </Description>
          <OfficeSelector
            offices={adminOffices.data}
            value={selectedOffice}
            onChange={setOffice}
          />
        </Field>
      </Card>

      <div className="grid min-w-0 grid-cols-1 gap-6 lg:grid-cols-[minmax(16rem,0.7fr)_minmax(0,1.5fr)]">
        <Card className="min-w-0 p-0">
          <div className="flex items-center justify-between border-b border-zinc-200 px-5 py-4">
            <H3>Templates</H3>
            <Badge color="blue">{sortedTemplates.length}</Badge>
          </div>
          <div className="space-y-2 p-3">
            {templates.isLoading ? (
              <>
                <Skeleton className="h-20 w-full" />
                <Skeleton className="h-20 w-full" />
              </>
            ) : sortedTemplates.length ? (
              sortedTemplates.map((template) => (
                <button
                  key={template.id}
                  type="button"
                  aria-current={
                    template.id === selectedTemplateId ? "true" : undefined
                  }
                  className={`w-full rounded-lg border p-4 text-left ${
                    template.id === selectedTemplateId
                      ? "border-blue-600 bg-blue-50"
                      : "border-zinc-200 hover:border-blue-300"
                  }`}
                  onClick={() => selectTemplate(template)}
                >
                  <div className="flex items-center justify-between gap-2">
                    <strong>{template.slug}</strong>
                    <Badge color={template.active ? "green" : "zinc"}>
                      {template.active ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                  <Text className="mt-1 line-clamp-2">
                    {template.subjectTemplate}
                  </Text>
                </button>
              ))
            ) : (
              <div className="p-5 text-center">
                <FaEnvelope className="mx-auto mb-3 text-2xl text-zinc-500" />
                <Text>No email templates exist for {selectedOffice}.</Text>
              </div>
            )}
          </div>
        </Card>

        <Card className="min-w-0 p-5">
          <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
            <div>
              <H3>{templateForm.id ? "Edit template" : "New template"}</H3>
              <Text>
                {dirty ? "Unsaved changes" : `Office: ${selectedOffice}`}
              </Text>
            </div>
            {templateForm.id &&
              (deleteConfirm ? (
                <div className="flex flex-wrap items-center gap-2">
                  <Text>Delete this template?</Text>
                  <Button
                    type="button"
                    color="danger"
                    disabled={pending}
                    onClick={async () => {
                      await deleteTemplate.mutateAsync(templateForm.id);
                      setSelectedTemplateId("");
                      setTemplateForm(emptyTemplate(selectedOffice));
                      setDeleteConfirm(false);
                      resetPreview();
                      toast.success("Template deleted");
                    }}
                  >
                    Confirm delete
                  </Button>
                  <Button
                    type="button"
                    color="light"
                    onClick={() => setDeleteConfirm(false)}
                  >
                    Cancel
                  </Button>
                </div>
              ) : (
                <Button
                  type="button"
                  color="danger"
                  style="outline"
                  onClick={() => setDeleteConfirm(true)}
                >
                  Delete template
                </Button>
              ))}
          </div>

          <form onSubmit={saveTemplate}>
            <Fieldset className="flex flex-col gap-5">
              <Field>
                <div className="flex items-center gap-1">
                  <Label htmlFor="template-slug">Template ID</Label>
                  <HelpTip title="Template ID">
                    This stable, office-scoped name identifies the template in
                    notification rules. Use lowercase letters, numbers, hyphens,
                    or underscores.
                  </HelpTip>
                </div>
                <Description>
                  A stable identifier such as job_failure_v1.
                </Description>
                <Input
                  required
                  id="template-slug"
                  maxLength={128}
                  value={templateForm.slug}
                  onChange={(event: React.ChangeEvent<HTMLInputElement>) =>
                    setTemplateForm((current) => ({
                      ...current,
                      slug: event.target.value.toLowerCase(),
                    }))
                  }
                />
              </Field>
              <Field>
                <div className="flex items-center gap-1">
                  <Label htmlFor="template-subject">Subject</Label>
                  <TemplateVariablesHelp />
                </div>
                <JinjaTemplateField
                  id="template-subject"
                  value={templateForm.subjectTemplate}
                  className="h-20"
                  onChange={(subjectTemplate) =>
                    setTemplateForm((current) => ({
                      ...current,
                      subjectTemplate,
                    }))
                  }
                />
              </Field>
              <Field>
                <div className="flex items-center gap-1">
                  <Label htmlFor="template-body">Body</Label>
                  <TemplateVariablesHelp />
                </div>
                <JinjaTemplateField
                  id="template-body"
                  value={templateForm.bodyTemplate}
                  onChange={(bodyTemplate) =>
                    setTemplateForm((current) => ({
                      ...current,
                      bodyTemplate,
                    }))
                  }
                />
              </Field>
              <Checkboxes
                key={`template-active-${templateForm.id || "new"}`}
                legend="Template status"
                content={[
                  {
                    id: "template-active",
                    label: "Active",
                    defaultChecked: templateForm.active,
                    onChange: (event: React.ChangeEvent<HTMLInputElement>) =>
                      setTemplateForm((current) => ({
                        ...current,
                        active: event.target.checked,
                      })),
                  },
                ]}
              />
              <div className="flex flex-wrap gap-3">
                <Button
                  type="submit"
                  disabled={
                    pending ||
                    !dirty ||
                    !templateForm.slug.trim() ||
                    !templateForm.subjectTemplate.trim() ||
                    !templateForm.bodyTemplate.trim()
                  }
                >
                  {templateForm.id ? "Save changes" : "Create template"}
                </Button>
                <Button
                  type="button"
                  color="light"
                  disabled={!templateForm.id || pending}
                  onClick={renderPreview}
                >
                  Preview email
                </Button>
              </div>
            </Fieldset>
          </form>

          {preview.data && (
            <section className="mt-6 rounded-lg border border-zinc-200 bg-white p-5">
              <Badge color="blue">Preview</Badge>
              <H3 className="mt-3 text-lg">{preview.data.subject}</H3>
              <pre className="mt-3 max-h-96 overflow-auto whitespace-pre-wrap rounded-lg bg-zinc-50 p-4 font-sans text-sm">
                {preview.data.body}
              </pre>
            </section>
          )}
        </Card>
      </div>
    </section>
  );
};
