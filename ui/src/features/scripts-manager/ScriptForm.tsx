import dayjs from "dayjs";
import { ViewField } from "./ViewField";
import {
  Button,
  Checkboxes,
  DeleteConfirm,
  Field,
  Fieldset,
  Input,
  Label,
  Text,
} from "@usace/groundwork";
import type { Script, ScriptFormData } from "../scripts-manager/types";
import { MdErrorOutline } from "react-icons/md";
import { useState } from "react";
import { RoleMultiSelect } from "./RoleMultiSelect";
import { allRoles } from "./utils";

const slugify = (str: string) => {
  return str
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/[\s_-]+/g, "-")
    .replace(/^-+|-+$/g, "");
};

const FormRow = ({ children }: React.PropsWithChildren) => {
  return <Field className="grid grid-cols-[120px_1fr] gap-6">{children}</Field>;
};

const InputLabel = ({
  htmlFor,
  children,
}: React.PropsWithChildren<{ htmlFor: string }>) => {
  return (
    <Label className="mt-4" htmlFor={htmlFor}>
      {children}
    </Label>
  );
};

interface ScriptFormProps {
  script?: Script;
  isPending: boolean;
  mutationError: Error | null;
  onDelete: (scriptId: string) => void;
  onSave: (data: ScriptFormData) => void;
  onCancelEdit: () => void;
}

export const ScriptForm = ({
  script,
  isPending,
  mutationError,
  onDelete,
  onSave,
  onCancelEdit,
}: ScriptFormProps) => {
  const [form, setForm] = useState<ScriptFormData>({
    name: script?.name ?? "",
    description: script?.description ?? "",
    active: script?.active ?? true,
    repoPath: script?.repoPath ?? "",
    runtime: script?.runtime ?? "python",
    resourceProfile: script?.resourceProfile ?? "small",
    envVars: script?.envVars ?? {},
    secretEnvNames: script?.secretEnvNames ?? [],
    roles: script?.roles ?? ["CWMS Users"],
  });
  const [envVarsText, setEnvVarsText] = useState(
    JSON.stringify(script?.envVars ?? {}, null, 2),
  );
  const [secretEnvNamesText, setSecretEnvNamesText] = useState(
    (script?.secretEnvNames ?? []).join("\n"),
  );
  const [formError, setFormError] = useState<string | null>(null);

  const handleSubmit = () => {
    try {
      const parsedEnvVars = JSON.parse(envVarsText || "{}");
      if (
        parsedEnvVars === null ||
        Array.isArray(parsedEnvVars) ||
        typeof parsedEnvVars !== "object"
      ) {
        setFormError("Environment variables must be a JSON object");
        return;
      }
      const secretEnvNames = secretEnvNamesText
        .split(/[,\n]/)
        .map((value) => value.trim())
        .filter(Boolean);

      setFormError(null);
      onSave({
        ...form,
        envVars: parsedEnvVars,
        secretEnvNames,
      });
    } catch {
      setFormError("Environment variables must be valid JSON");
    }
  };

  const update = <K extends keyof typeof form>(
    key: K,
    value: (typeof form)[K],
  ) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        e.stopPropagation();
        handleSubmit();
      }}
    >
      <div className="flex flex-col gap-y-6">
        <Fieldset disabled={isPending} className="flex flex-col gap-2">
          <ViewField label="Id">{script?.id ?? "<unassigned>"}</ViewField>
          <FormRow>
            <InputLabel htmlFor="name">Name</InputLabel>
            <Input
              id="name"
              name="name"
              value={form.name}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                update("name", e.target.value);
              }}
              required
            />
          </FormRow>
          <ViewField label="Slug">
            {script?.slug ?? slugify(form.name)}
          </ViewField>
          <FormRow>
            <InputLabel htmlFor="description">Description</InputLabel>
            <Input
              id="description"
              name="description"
              value={form.description}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                update("description", e.target.value)
              }
            />
          </FormRow>
          <FormRow>
            <InputLabel htmlFor="repoPath">GitHub Repo Path</InputLabel>
            <Input
              id="repoPath"
              name="repoPath"
              value={form.repoPath}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                update("repoPath", e.target.value)
              }
              required
            />
          </FormRow>
          <ViewField label="Execution Type">
            {script?.executionType ?? "python"}
          </ViewField>
          <FormRow>
            <InputLabel htmlFor="runtime">Runtime</InputLabel>
            <Input
              id="runtime"
              name="runtime"
              value={form.runtime}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                update("runtime", e.target.value)
              }
              required
            />
          </FormRow>
          <FormRow>
            <InputLabel htmlFor="resourceProfile">Resource Profile</InputLabel>
            <Input
              id="resourceProfile"
              name="resourceProfile"
              value={form.resourceProfile}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                update("resourceProfile", e.target.value)
              }
              required
            />
          </FormRow>
          <FormRow>
            <Label htmlFor="roles">Roles</Label>
            <RoleMultiSelect
              allRoles={allRoles}
              initialSelectedRoles={form.roles}
              onChange={(selectedRoles) => update("roles", selectedRoles)}
            />
          </FormRow>
          <FormRow>
            <InputLabel htmlFor="envVars">Environment Variables</InputLabel>
            <textarea
              id="envVars"
              name="envVars"
              className="min-h-32 rounded border border-gray-400 p-2 font-mono text-sm"
              value={envVarsText}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                setEnvVarsText(e.target.value)
              }
            />
          </FormRow>
          <FormRow>
            <InputLabel htmlFor="secretEnvNames">Secret Names</InputLabel>
            <textarea
              id="secretEnvNames"
              name="secretEnvNames"
              className="min-h-24 rounded border border-gray-400 p-2 font-mono text-sm"
              value={secretEnvNamesText}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                setSecretEnvNamesText(e.target.value)
              }
            />
          </FormRow>
          <FormRow>
            <Label htmlFor="active">Active</Label>
            <Checkboxes
              content={[
                {
                  id: "active",
                  defaultChecked: script?.active ?? true,
                  onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
                    update("active", e.target.checked),
                },
              ]}
            />
          </FormRow>
          {script && (
            <>
              <ViewField label="Created At">
                {dayjs(script?.createdTime).toString()}
              </ViewField>
              <ViewField label="Last Update">
                {dayjs(script?.updatedTime).toString()}
              </ViewField>
            </>
          )}
        </Fieldset>
        <div className="w-full flex justify-between">
          {script && <DeleteConfirm onDelete={() => onDelete(script?.id)} />}
          <div className="flex justify-between gap-6 ml-auto">
            <Button type="submit" disabled={isPending}>
              Save
            </Button>
            <Button type="button" disabled={isPending} onClick={onCancelEdit}>
              Cancel
            </Button>
          </div>
        </div>
        {(formError || mutationError) && (
          <div className="flex gap-2">
            <MdErrorOutline className="text-red-500 flex-none size-6" />
            <Text className="text-red-500">
              {formError ?? mutationError?.message}
            </Text>
          </div>
        )}
      </div>
    </form>
  );
};
