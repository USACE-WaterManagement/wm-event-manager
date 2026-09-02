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
import { HelpTip } from "../../shared/components/HelpTip";

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
    roles: script?.roles ?? ["CWMS Users"],
  });

  const handleSubmit = () => onSave(form);

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
            <div className="flex items-start gap-1">
              <InputLabel htmlFor="repoPath">GitHub Repo Path</InputLabel>
              <HelpTip title="Repository path" className="mt-2">
                Enter the path to the runnable file inside the configured GitHub
                repository, such as <code>bin/hourly.sh</code>. Do not enter a
                repository URL.
              </HelpTip>
            </div>
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
            <div className="flex items-center gap-1 self-start">
              <Label htmlFor="roles">Roles</Label>
              <HelpTip title="Allowed roles">
                A user needs at least one selected role in this script&apos;s
                office to view or run it. Select CWMS Users when every
                authorized office user should have access.
              </HelpTip>
            </div>
            <RoleMultiSelect
              allRoles={allRoles}
              initialSelectedRoles={form.roles}
              onChange={(selectedRoles) => update("roles", selectedRoles)}
            />
          </FormRow>
          <FormRow>
            <div className="flex items-center gap-1 self-start">
              <Label htmlFor="active">Active</Label>
              <HelpTip title="Active scripts">
                Active scripts can appear in authorized script lists and be
                submitted. Clear this while a script should remain configured
                but unavailable to users.
              </HelpTip>
            </div>
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
        {mutationError && (
          <div className="flex gap-2">
            <MdErrorOutline className="text-red-500 flex-none size-6" />
            <Text className="text-red-500">{mutationError.message}</Text>
          </div>
        )}
      </div>
    </form>
  );
};
