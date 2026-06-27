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
import {
  MdAdd,
  MdClose,
  MdDelete,
  MdDescription,
  MdFolder,
  MdHelpOutline,
} from "react-icons/md";
import { useEffect, useState } from "react";
import { RoleMultiSelect } from "./RoleMultiSelect";
import { useAuth } from "@usace-watermanagement/groundwork-water";
import fetchWithAuth from "../../utils/fetchWithAuth";
import {
  allRoles,
  availableScheduleTimezones,
  defaultScheduleTimezone,
  isValidScheduleTimezone,
  resourceProfileLabels,
  scheduleTimezoneLabel,
} from "./utils";

const slugify = (str: string) => {
  return str
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/[\s_-]+/g, "-")
    .replace(/^-+|-+$/g, "");
};

const FormRow = ({ children }: React.PropsWithChildren) => {
  return (
    <Field className="grid grid-cols-1 items-start gap-1 md:grid-cols-[150px_minmax(0,1fr)] md:gap-x-3 md:gap-y-2">
      {children}
    </Field>
  );
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

// Mirror API/runtime reserved names and surface conflicts before submit.
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

const normalizedExecutionType = (executionType?: string | null) =>
  executionType === "command" ? "command" : "github_file";

const runtimeScriptTypes: Record<string, string[]> = {
  python: [".py"],
  node: [".js", ".mjs", ".cjs", ".ts"],
  java: [".java", ".jar"],
  shell: [".sh", ".bash", ".zsh", "extensionless"],
};

type RepositoryEntry = {
  name: string;
  path: string;
  entryType: "directory" | "file";
  selectable: boolean;
  runtimeMatch: boolean;
};

type RepositoryBrowserResponse = {
  directory: string;
  configured: boolean;
  scriptTypes: string[];
  entries: RepositoryEntry[];
};

const directoryFromPath = (path: string) => {
  const normalizedPath = path.replace(/\\/g, "/");
  if (normalizedPath.endsWith("/")) {
    return normalizedPath.replace(/\/+$/, "");
  }
  const lastSlash = normalizedPath.lastIndexOf("/");
  return lastSlash > -1 ? normalizedPath.slice(0, lastSlash) : "";
};

const parentDirectory = (path: string) => {
  const normalizedPath = path.replace(/\\/g, "/").replace(/\/+$/, "");
  const lastSlash = normalizedPath.lastIndexOf("/");
  return lastSlash > -1 ? normalizedPath.slice(0, lastSlash) : "";
};

const InputLabel = ({
  htmlFor,
  children,
}: React.PropsWithChildren<{ htmlFor: string }>) => {
  return (
    <Label className="mt-2" htmlFor={htmlFor}>
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
  const auth = useAuth();
  const [form, setForm] = useState<ScriptFormData>({
    name: script?.name ?? "",
    description: script?.description ?? "",
    active: script?.active ?? true,
    executionType: normalizedExecutionType(script?.executionType),
    repoPath: script?.repoPath ?? "",
    runtime: script?.runtime ?? "python",
    resourceProfile: script?.resourceProfile ?? "small",
    commandArgs: script?.commandArgs ?? [],
    timeoutMinutes: script?.timeoutMinutes ?? 30,
    scheduleEnabled: script?.scheduleEnabled ?? false,
    scheduleType: script?.scheduleType ?? "manual",
    scheduleMinute: script?.scheduleMinute ?? 15,
    scheduleCron: script?.scheduleCron ?? "",
    scheduleTimezone: script?.scheduleTimezone ?? defaultScheduleTimezone,
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
  const [repoSuggestions, setRepoSuggestions] =
    useState<RepositoryBrowserResponse | null>(null);
  const [repoSuggestionsLoading, setRepoSuggestionsLoading] = useState(false);
  const [repoBrowser, setRepoBrowser] =
    useState<RepositoryBrowserResponse | null>(null);
  const [repoBrowserLoading, setRepoBrowserLoading] = useState(false);
  const [repoBrowserDirectory, setRepoBrowserDirectory] = useState(
    directoryFromPath(script?.repoPath ?? ""),
  );
  const [repoBrowserOpen, setRepoBrowserOpen] = useState(false);

  const fetchRepositoryEntries = async (
    directory: string,
    includeAllFiles: boolean,
  ) => {
    const params = new URLSearchParams({
      directory,
      runtime: form.runtime,
      includeAll: includeAllFiles ? "true" : "false",
    });
    const response = await fetchWithAuth(
      `/api/scripts/repository?${params.toString()}`,
      {},
      auth.token,
    );
    if (!response.ok) {
      throw new Error("Failed to fetch repository paths");
    }
    return response.json() as Promise<RepositoryBrowserResponse>;
  };

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

    const normalizedScheduleTimezone = form.scheduleTimezone.trim();
    if (!isValidScheduleTimezone(normalizedScheduleTimezone)) {
      setFormError(`Schedule timezone "${form.scheduleTimezone}" is not valid`);
      return;
    }

    setFormError(null);
    onSave({
      ...form,
      executionType: normalizedExecutionType(form.executionType),
      commandArgs,
      scheduleTimezone: normalizedScheduleTimezone,
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
  const isCommandExecution =
    normalizedExecutionType(form.executionType) === "command";
  const currentScheduleTimezone = scheduleTimezoneLabel(form.scheduleTimezone);
  const scriptTypes = runtimeScriptTypes[form.runtime] ?? [];
  const formTitle = script ? `Edit Script: ${script.name}` : "New Script";
  const submitLabel = script ? "Save changes" : "Create script";

  useEffect(() => {
    if (isCommandExecution) {
      setRepoSuggestions(null);
      setRepoSuggestionsLoading(false);
      return;
    }

    const requestedDirectory = directoryFromPath(form.repoPath);
    const handle = window.setTimeout(() => {
      setRepoSuggestionsLoading(true);
      fetchRepositoryEntries(requestedDirectory, false)
        .then(setRepoSuggestions)
        .catch(() => setRepoSuggestions(null))
        .finally(() => setRepoSuggestionsLoading(false));
    }, 300);

    return () => window.clearTimeout(handle);
  }, [auth.token, form.repoPath, form.runtime, isCommandExecution]);

  useEffect(() => {
    if (!repoBrowserOpen || isCommandExecution) {
      return;
    }

    setRepoBrowserLoading(true);
    fetchRepositoryEntries(repoBrowserDirectory, true)
      .then(setRepoBrowser)
      .catch(() => setRepoBrowser(null))
      .finally(() => setRepoBrowserLoading(false));
  }, [
    auth.token,
    form.runtime,
    isCommandExecution,
    repoBrowserDirectory,
    repoBrowserOpen,
  ]);

  const selectRepositoryEntry = (entry: RepositoryEntry) => {
    if (entry.entryType === "directory") {
      const directoryPath = entry.path.replace(/\/+$/, "");
      setRepoBrowserDirectory(directoryPath);
      update("repoPath", directoryPath ? `${directoryPath}/` : "");
      return;
    }
    update("repoPath", entry.path);
    setRepoBrowserOpen(false);
  };

  const openRepositoryBrowser = () => {
    setRepoBrowserDirectory(directoryFromPath(form.repoPath));
    setRepoBrowserOpen(true);
  };

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        e.stopPropagation();
        handleSubmit();
      }}
    >
      <div className="flex max-h-[65vh] flex-col overflow-hidden">
        <div className="sticky top-0 z-20 flex flex-wrap items-center justify-between gap-3 border-b border-gray-300 bg-gray-100 pb-3">
          <div className="min-w-0">
            <h3 className="truncate text-lg font-semibold">{formTitle}</h3>
            <Text className="text-sm text-gray-600">
              Configure runtime, source, schedule, roles, and environment.
            </Text>
          </div>
          <div className="flex flex-wrap items-center justify-end gap-3">
            {script && <DeleteConfirm onDelete={() => onDelete(script?.id)} />}
            <Button type="submit" disabled={isPending}>
              {submitLabel}
            </Button>
            <Button type="button" disabled={isPending} onClick={onCancelEdit}>
              Cancel
            </Button>
          </div>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto pt-4 pr-2">
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
            <InputLabel htmlFor="executionType">Source</InputLabel>
            <div className="max-w-56 min-w-0">
              <Dropdown
                id="executionType"
                name="executionType"
                className="w-full"
                value={normalizedExecutionType(form.executionType)}
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
                  update("executionType", e.target.value)
                }
                options={[
                  <option key="github_file" value="github_file">
                    GitHub File Path
                  </option>,
                  <option key="command" value="command">
                    Command
                  </option>,
                ]}
              />
            </div>
          </FormRow>
          <FormRow>
            <InputLabel htmlFor="repoPath">
              {isCommandExecution ? "Command" : "GitHub File Path"}
            </InputLabel>
            <div className="min-w-0">
              <div className={isCommandExecution ? "" : "flex gap-2"}>
                <Input
                  id="repoPath"
                  name="repoPath"
                  className="min-w-0 flex-1"
                  placeholder={
                    isCommandExecution
                      ? "cwms-cli users list | grep Test"
                      : "bin/hourly.sh"
                  }
                  value={form.repoPath}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                    update("repoPath", e.target.value)
                  }
                  required
                />
                {!isCommandExecution && (
                  <Button type="button" onClick={openRepositoryBrowser}>
                    Browse
                  </Button>
                )}
              </div>
              {!isCommandExecution && (
                <div className="mt-2 flex flex-col gap-2">
                  <Text className="text-xs text-gray-600">
                    {form.runtime} scripts: {scriptTypes.join(", ")}{" "}
                    (case-insensitive)
                  </Text>
                  <div className="rounded border border-gray-300 bg-white">
                    <div className="border-b border-gray-200 px-2 py-1 text-xs font-semibold text-gray-600">
                      Available in /{directoryFromPath(form.repoPath)}
                    </div>
                    {repoSuggestionsLoading ? (
                      <div className="px-2 py-2 text-sm text-gray-600">
                        Loading paths...
                      </div>
                    ) : repoSuggestions && !repoSuggestions.configured ? (
                      <div className="px-2 py-2 text-sm text-gray-600">
                        Repository browser is not configured.
                      </div>
                    ) : repoSuggestions?.entries.length ? (
                      <div className="max-h-32 overflow-y-auto">
                        {repoSuggestions.entries.map((entry) => (
                          <button
                            key={`${entry.entryType}-${entry.path}`}
                            className="flex w-full items-center gap-2 px-2 py-1 text-left text-sm hover:bg-blue-50"
                            title={entry.path}
                            type="button"
                            onClick={() => selectRepositoryEntry(entry)}
                          >
                            {entry.entryType === "directory" ? (
                              <MdFolder className="flex-none text-blue-700" />
                            ) : (
                              <MdDescription className="flex-none text-gray-600" />
                            )}
                            <span className="truncate">{entry.path}</span>
                          </button>
                        ))}
                      </div>
                    ) : (
                      <div className="px-2 py-2 text-sm text-gray-600">
                        No matching scripts found.
                      </div>
                    )}
                  </div>
                  {repoBrowserOpen && (
                    <div className="rounded border border-gray-400 bg-white">
                      <div className="flex items-center justify-between gap-2 border-b border-gray-200 px-2 py-2">
                        <div className="min-w-0">
                          <div className="text-sm font-semibold">
                            Browse repository
                          </div>
                          <div className="truncate text-xs text-gray-600">
                            /{repoBrowserDirectory}
                          </div>
                        </div>
                        <button
                          aria-label="Close repository browser"
                          className="rounded p-1 hover:bg-gray-100"
                          title="Close repository browser"
                          type="button"
                          onClick={() => setRepoBrowserOpen(false)}
                        >
                          <MdClose className="size-5" />
                        </button>
                      </div>
                      <div className="max-h-52 overflow-y-auto">
                        {repoBrowserDirectory && (
                          <button
                            className="flex w-full items-center gap-2 px-2 py-2 text-left text-sm hover:bg-blue-50"
                            type="button"
                            onClick={() =>
                              setRepoBrowserDirectory(
                                parentDirectory(repoBrowserDirectory),
                              )
                            }
                          >
                            <MdFolder className="flex-none text-blue-700" />
                            <span>..</span>
                          </button>
                        )}
                        {repoBrowserLoading ? (
                          <div className="px-2 py-3 text-sm text-gray-600">
                            Loading paths...
                          </div>
                        ) : repoBrowser && !repoBrowser.configured ? (
                          <div className="px-2 py-3 text-sm text-gray-600">
                            Repository browser is not configured.
                          </div>
                        ) : repoBrowser?.entries.length ? (
                          repoBrowser.entries.map((entry) => (
                            <button
                              key={`${entry.entryType}-${entry.path}`}
                              className="flex w-full items-center gap-2 px-2 py-2 text-left text-sm hover:bg-blue-50"
                              title={entry.path}
                              type="button"
                              onClick={() => selectRepositoryEntry(entry)}
                            >
                              {entry.entryType === "directory" ? (
                                <MdFolder className="flex-none text-blue-700" />
                              ) : (
                                <MdDescription className="flex-none text-gray-600" />
                              )}
                              <span className="truncate">{entry.name}</span>
                              {entry.entryType === "file" && entry.runtimeMatch && (
                                <span className="ml-auto flex-none rounded bg-green-100 px-2 py-0.5 text-xs text-green-800">
                                  runtime
                                </span>
                              )}
                            </button>
                          ))
                        ) : (
                          <div className="px-2 py-3 text-sm text-gray-600">
                            No paths found.
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </FormRow>
          <FormRow>
            <InputLabel htmlFor="runtime">Runtime</InputLabel>
            <div className="max-w-44 min-w-0">
              <Dropdown
                id="runtime"
                name="runtime"
                className="w-full"
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
            </div>
          </FormRow>
          <FormRow>
            <InputLabel htmlFor="resourceProfile">Resource Profile</InputLabel>
            <div className="max-w-80 min-w-0">
              <Dropdown
                id="resourceProfile"
                name="resourceProfile"
                className="w-full"
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
            </div>
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
            <InputLabel htmlFor="commandArgs">
              {isCommandExecution ? "Appended Args" : "Command Args"}
            </InputLabel>
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
            <Label className="md:mt-2" htmlFor="scheduleEnabled">
              Schedule ({currentScheduleTimezone})
            </Label>
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
                <InputLabel htmlFor="scheduleTimezone">Timezone</InputLabel>
                <div className="min-w-0">
                  <Input
                    id="scheduleTimezone"
                    list="schedule-timezone-options"
                    name="scheduleTimezone"
                    value={form.scheduleTimezone}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                      update("scheduleTimezone", e.target.value)
                    }
                    required
                  />
                  <datalist id="schedule-timezone-options">
                    {availableScheduleTimezones.map((timezone) => (
                      <option key={timezone} value={timezone} />
                    ))}
                  </datalist>
                </div>
              </FormRow>
              <FormRow>
                <InputLabel htmlFor="scheduleType">Schedule Type</InputLabel>
                <div className="max-w-56 min-w-0">
                  <Dropdown
                    id="scheduleType"
                    name="scheduleType"
                    className="w-full"
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
                </div>
              </FormRow>
              {form.scheduleType === "hourly" && (
                <FormRow>
                  <InputLabel htmlFor="scheduleMinute">
                    Minute ({currentScheduleTimezone})
                  </InputLabel>
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
                  <div className="flex items-center gap-1">
                    <InputLabel htmlFor="scheduleCron">
                      Cron ({currentScheduleTimezone})
                    </InputLabel>
                    <a
                      aria-label="Open cron expression helper"
                      className="mt-4 inline-flex text-blue-700 hover:text-blue-900"
                      href="https://crontab.guru/"
                      rel="noreferrer"
                      target="_blank"
                      title="Open cron expression helper in a new tab"
                    >
                      <MdHelpOutline className="size-5" />
                    </a>
                  </div>
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
        {(formError || mutationError) && (
          <div className="mt-4 flex gap-2">
            <MdErrorOutline className="text-red-500 flex-none size-6" />
            <Text className="text-red-500">
              {formError ?? mutationError?.message}
            </Text>
          </div>
        )}
        </div>
      </div>
    </form>
  );
};
