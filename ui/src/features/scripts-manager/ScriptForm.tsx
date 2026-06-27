import dayjs from "dayjs";
import { ViewField } from "./ViewField";
import {
  Button,
  Checkboxes,
  DeleteConfirm,
  Dropdown,
  Field,
  Fieldset,
  Input,
  Label,
  Text,
} from "@usace/groundwork";
import type { Script, ScriptFormData } from "../scripts-manager/types";
import { MdErrorOutline } from "react-icons/md";
import { MdAdd, MdDelete } from "react-icons/md";
import { useState } from "react";
import { RoleMultiSelect } from "./RoleMultiSelect";
import { allRoles, resourceProfileLabels } from "./utils";

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

type EnvVarRow = {
  id: string;
  key: string;
  value: string;
};

const newEnvVarRow = (): EnvVarRow => ({
  id: `env-${Date.now()}-${Math.random().toString(36).slice(2)}`,
  key: "",
  value: "",
});

const envVarsToRows = (envVars?: Record<string, string>): EnvVarRow[] =>
  Object.entries(envVars ?? {}).map(([key, value], index) => ({
    id: `env-${index}-${key}`,
    key,
    value: value ?? "",
  }));

const isAwsBatchReservedEnvName = (name: string) =>
  name.trim().toUpperCase().startsWith("AWS_BATCH");

const batchEventsReservedEnvNames = new Set([
  "BATCH_JOB_CONTEXT_TOKEN",
  "ENVIRONMENT",
  "GITHUB_BRANCH",
  "GITHUB_TOKEN",
  "JOB_ID",
  "OFFICE",
  "REPO_PATH",
  "RUNTIME",
  "SCRIPT_PATH",
  "SCRIPT_SLUG",
  "SKIP_GIT_CLONE",
]);

const isBatchEventsReservedEnvName = (name: string) => {
  const normalizedName = name.trim().toUpperCase();
  return (
    normalizedName.startsWith("AWS_BATCH") ||
    normalizedName.startsWith("BATCH_EVENTS_") ||
    batchEventsReservedEnvNames.has(normalizedName)
  );
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
    commandArgs: script?.commandArgs ?? [],
    timeoutMinutes: script?.timeoutMinutes ?? 30,
    scheduleEnabled: script?.scheduleEnabled ?? false,
    scheduleType: script?.scheduleType ?? "manual",
    scheduleMinute: script?.scheduleMinute ?? 15,
    scheduleCron: script?.scheduleCron ?? "",
    envVars: script?.envVars ?? {},
    secretEnvNames: script?.secretEnvNames ?? [],
    roles: script?.roles ?? ["CWMS Users"],
  });
  const [envVarRows, setEnvVarRows] = useState<EnvVarRow[]>(
    envVarsToRows(script?.envVars),
  );
  const [secretEnvNamesText, setSecretEnvNamesText] = useState(
    (script?.secretEnvNames ?? []).join("\n"),
  );
  const [commandArgsText, setCommandArgsText] = useState(
    (script?.commandArgs ?? []).join("\n"),
  );
  const [formError, setFormError] = useState<string | null>(null);

  const handleSubmit = () => {
    const envVars: Record<string, string> = {};
    const usedKeys = new Set<string>();

    for (const row of envVarRows) {
      const key = row.key.trim();
      const value = row.value;

      if (!key && !value.trim()) {
        continue;
      }

      if (!key) {
        setFormError("Environment variable keys cannot be blank");
        return;
      }

      if (usedKeys.has(key)) {
        setFormError(`Environment variable key "${key}" is duplicated`);
        return;
      }

      if (isAwsBatchReservedEnvName(key)) {
        setFormError(
          `Environment variable key "${key}" cannot start with AWS_BATCH`,
        );
        return;
      }

      if (isBatchEventsReservedEnvName(key)) {
        setFormError(
          `Environment variable key "${key}" is reserved for Batch Events runtime`,
        );
        return;
      }

      usedKeys.add(key);
      envVars[key] = value;
    }

    const secretEnvNames = secretEnvNamesText
      .split(/[,\n]/)
      .map((value) => value.trim())
      .filter(Boolean);
    const commandArgs = commandArgsText
      .split(/\n/)
      .map((value) => value.trim())
      .filter(Boolean);
    const reservedSecretEnvName = secretEnvNames.find(isAwsBatchReservedEnvName);
    if (reservedSecretEnvName) {
      setFormError(
        `Secret environment variable "${reservedSecretEnvName}" cannot start with AWS_BATCH`,
      );
      return;
    }
    const batchEventsReservedSecretEnvName = secretEnvNames.find(
      isBatchEventsReservedEnvName,
    );
    if (batchEventsReservedSecretEnvName) {
      setFormError(
        `Secret environment variable "${batchEventsReservedSecretEnvName}" is reserved for Batch Events runtime`,
      );
      return;
    }

    setFormError(null);
    onSave({
      ...form,
      commandArgs,
      scheduleCron:
        form.scheduleEnabled && form.scheduleType === "cron"
          ? form.scheduleCron?.trim()
          : null,
      scheduleMinute:
        form.scheduleEnabled && form.scheduleType === "hourly"
          ? form.scheduleMinute
          : null,
      scheduleType: form.scheduleEnabled ? form.scheduleType : "manual",
      envVars,
      secretEnvNames,
    });
  };

  const update = <K extends keyof typeof form>(
    key: K,
    value: (typeof form)[K],
  ) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const updateEnvVarRow = (
    rowId: string,
    field: "key" | "value",
    value: string,
  ) => {
    setEnvVarRows((rows) =>
      rows.map((row) => (row.id === rowId ? { ...row, [field]: value } : row)),
    );
  };

  const deleteEnvVarRow = (rowId: string) => {
    setEnvVarRows((rows) => rows.filter((row) => row.id !== rowId));
  };

  const updateScheduleEnabled = (enabled: boolean) => {
    setForm((prev) => ({
      ...prev,
      scheduleEnabled: enabled,
      scheduleType:
        enabled && prev.scheduleType === "manual" ? "hourly" : prev.scheduleType,
      scheduleMinute: enabled ? (prev.scheduleMinute ?? 15) : prev.scheduleMinute,
    }));
  };

  const envVarKeyCounts = envVarRows.reduce<Record<string, number>>(
    (counts, row) => {
      const key = row.key.trim();
      if (key) {
        counts[key] = (counts[key] ?? 0) + 1;
      }
      return counts;
    },
    {},
  );

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
          <FormRow>
            <InputLabel htmlFor="runtime">Runtime</InputLabel>
            <Dropdown
              id="runtime"
              name="runtime"
              value={form.runtime}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                update("runtime", e.target.value)
              }
              options={[
                <option key="python" value="python">
                  Python
                </option>,
                <option key="node" value="node">
                  Node
                </option>,
                <option key="java" value="java">
                  Java
                </option>,
                <option key="shell" value="shell">
                  Shell
                </option>,
              ]}
            />
          </FormRow>
          <FormRow>
            <InputLabel htmlFor="resourceProfile">Resource Profile</InputLabel>
            <Dropdown
              id="resourceProfile"
              name="resourceProfile"
              value={form.resourceProfile}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                update("resourceProfile", e.target.value)
              }
              options={[
                <option key="small" value="small">
                  {resourceProfileLabels.small}
                </option>,
                <option key="medium" value="medium">
                  {resourceProfileLabels.medium}
                </option>,
                <option key="large" value="large">
                  {resourceProfileLabels.large}
                </option>,
              ]}
            />
          </FormRow>
          <FormRow>
            <InputLabel htmlFor="timeoutMinutes">Timeout</InputLabel>
            <Input
              id="timeoutMinutes"
              max={1440}
              min={1}
              name="timeoutMinutes"
              type="number"
              value={form.timeoutMinutes}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                update("timeoutMinutes", Number(e.target.value))
              }
              required
            />
          </FormRow>
          <FormRow>
            <InputLabel htmlFor="commandArgs">Command Args</InputLabel>
            <textarea
              id="commandArgs"
              name="commandArgs"
              className="min-h-24 rounded border border-gray-400 p-2 font-mono text-sm"
              value={commandArgsText}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                setCommandArgsText(e.target.value)
              }
            />
          </FormRow>
          <FormRow>
            <Label htmlFor="scheduleEnabled">Schedule</Label>
            <Checkboxes
              content={[
                {
                  id: "scheduleEnabled",
                  defaultChecked: form.scheduleEnabled,
                  onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
                    updateScheduleEnabled(e.target.checked),
                },
              ]}
            />
          </FormRow>
          {form.scheduleEnabled && (
            <>
              <FormRow>
                <InputLabel htmlFor="scheduleType">Schedule Type</InputLabel>
                <Dropdown
                  id="scheduleType"
                  name="scheduleType"
                  value={form.scheduleType}
                  onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                    update("scheduleType", e.target.value)
                  }
                  options={[
                    <option key="hourly" value="hourly">
                      Hourly
                    </option>,
                    <option key="cron" value="cron">
                      Cron
                    </option>,
                  ]}
                />
              </FormRow>
              {form.scheduleType === "hourly" && (
                <FormRow>
                  <InputLabel htmlFor="scheduleMinute">Minute</InputLabel>
                  <Input
                    id="scheduleMinute"
                    max={59}
                    min={0}
                    name="scheduleMinute"
                    type="number"
                    value={form.scheduleMinute ?? 15}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                      update("scheduleMinute", Number(e.target.value))
                    }
                    required
                  />
                </FormRow>
              )}
              {form.scheduleType === "cron" && (
                <FormRow>
                  <InputLabel htmlFor="scheduleCron">Cron</InputLabel>
                  <Input
                    id="scheduleCron"
                    name="scheduleCron"
                    placeholder="0 17 * * *"
                    value={form.scheduleCron ?? ""}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                      update("scheduleCron", e.target.value)
                    }
                    required
                  />
                </FormRow>
              )}
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
            <InputLabel htmlFor="envVars">Environment Variables</InputLabel>
            <div className="flex flex-col gap-2">
              <div
                id="envVars"
                className="max-h-64 overflow-y-auto rounded border border-gray-400"
              >
                <div className="sticky top-0 grid grid-cols-[minmax(8rem,1fr)_minmax(10rem,1.5fr)_3.25rem] gap-2 border-b border-gray-300 bg-gray-100 px-2 py-1 pr-4 text-sm font-semibold">
                  <span>Key</span>
                  <span>Value</span>
                  <span className="sr-only">Delete</span>
                </div>
                {envVarRows.length === 0 ? (
                  <div className="px-2 py-3 text-sm text-gray-600">
                    No environment variables.
                  </div>
                ) : (
                  <div className="flex flex-col divide-y divide-gray-200">
                    {envVarRows.map((row) => {
                      const isDuplicate =
                        row.key.trim() !== "" &&
                        envVarKeyCounts[row.key.trim()] > 1;

                      return (
                        <div
                          className="grid grid-cols-[minmax(8rem,1fr)_minmax(10rem,1.5fr)_3.25rem] gap-2 px-2 py-2 pr-4"
                          key={row.id}
                        >
                          <Input
                            aria-label="Environment variable key"
                            className={
                              isDuplicate
                                ? "min-w-0 border-red-500"
                                : "min-w-0"
                            }
                            value={row.key}
                            onChange={(
                              e: React.ChangeEvent<HTMLInputElement>,
                            ) => updateEnvVarRow(row.id, "key", e.target.value)}
                          />
                          <Input
                            aria-label={`Value for ${row.key || "environment variable"}`}
                            className="min-w-0"
                            value={row.value}
                            onChange={(
                              e: React.ChangeEvent<HTMLInputElement>,
                            ) =>
                              updateEnvVarRow(row.id, "value", e.target.value)
                            }
                          />
                          <button
                            aria-label={`Delete ${row.key || "environment variable"}`}
                            className="focus:gw-ring-2 focus:gw-ring-red-700 focus:gw-ring-offset-2"
                            style={{
                              alignItems: "center",
                              backgroundColor: "#b91c1c",
                              borderRadius: "0.25rem",
                              color: "#ffffff",
                              display: "flex",
                              height: "2.25rem",
                              justifyContent: "center",
                              padding: 0,
                              width: "2.75rem",
                            }}
                            title="Delete environment variable"
                            type="button"
                            onClick={() => deleteEnvVarRow(row.id)}
                          >
                            <MdDelete style={{ fontSize: "1.25rem" }} />
                          </button>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
              <div>
                <Button
                  type="button"
                  onClick={() => setEnvVarRows((rows) => [...rows, newEnvVarRow()])}
                >
                  <MdAdd />
                  Add variable
                </Button>
              </div>
            </div>
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
