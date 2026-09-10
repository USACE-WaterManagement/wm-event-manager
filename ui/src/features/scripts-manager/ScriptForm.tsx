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
    scheduleEnabled: script?.scheduleEnabled ?? false,
    scheduleType: script?.scheduleType ?? "manual",
    scheduleMinute: script?.scheduleMinute ?? 0,
    scheduleCron: script?.scheduleCron ?? "",
    scheduleTimezone: script?.scheduleTimezone ?? "UTC",
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
            <InputLabel htmlFor="scheduleType">Schedule</InputLabel>
            <select
              id="scheduleType"
              className="rounded border p-2"
              value={form.scheduleType}
              onChange={(e) => {
                update("scheduleType", e.target.value);
                if (e.target.value === "manual")
                  update("scheduleEnabled", false);
              }}
            >
              <option value="manual">Manual only</option>
              <option value="hourly">Every hour</option>
              <option value="cron">Cron expression</option>
            </select>
          </FormRow>
          {form.scheduleType !== "manual" && (
            <>
              {form.scheduleType === "hourly" ? (
                <FormRow>
                  <InputLabel htmlFor="scheduleMinute">Minute</InputLabel>
                  <Input
                    id="scheduleMinute"
                    type="number"
                    min={0}
                    max={59}
                    required
                    value={form.scheduleMinute ?? ""}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                      update(
                        "scheduleMinute",
                        e.target.value === "" ? null : Number(e.target.value),
                      )
                    }
                  />
                </FormRow>
              ) : (
                <FormRow>
                  <InputLabel htmlFor="scheduleCron">
                    Cron expression
                  </InputLabel>
                  <div>
                    <Input
                      id="scheduleCron"
                      required
                      value={form.scheduleCron ?? ""}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                        update("scheduleCron", e.target.value)
                      }
                    />
                    <Text>
                      Minute, hour, day of month, month, day of week. For
                      example: 0 8 * * 1-5.
                    </Text>
                  </div>
                </FormRow>
              )}
              <FormRow>
                <InputLabel htmlFor="scheduleTimezone">Timezone</InputLabel>
                <div>
                  <Input
                    id="scheduleTimezone"
                    required
                    list="schedule-timezones"
                    value={form.scheduleTimezone}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                      update("scheduleTimezone", e.target.value)
                    }
                  />
                  <datalist id="schedule-timezones">
                    {[
                      "UTC",
                      "America/New_York",
                      "America/Chicago",
                      "America/Denver",
                      "America/Los_Angeles",
                      "America/Anchorage",
                      "Pacific/Honolulu",
                    ].map((zone) => (
                      <option key={zone} value={zone} />
                    ))}
                  </datalist>
                  <Text>
                    Use an IANA timezone. Missing daylight-saving times are
                    skipped; repeated times run once.
                  </Text>
                </div>
              </FormRow>
              <FormRow>
                <Label htmlFor="scheduleEnabled">Enable schedule</Label>
                <input
                  id="scheduleEnabled"
                  type="checkbox"
                  checked={form.scheduleEnabled}
                  onChange={(e) => update("scheduleEnabled", e.target.checked)}
                />
              </FormRow>
            </>
          )}
          <FormRow>
            <Label htmlFor="roles">Roles</Label>
            <RoleMultiSelect
              allRoles={allRoles}
              initialSelectedRoles={form.roles}
              onChange={(selectedRoles) => update("roles", selectedRoles)}
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
