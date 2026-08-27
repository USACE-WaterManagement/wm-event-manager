import dayjs from "dayjs";
import { ViewField } from "./ViewField";
import { Button, Text } from "@usace/groundwork";
import type { Script } from "../scripts-manager/types";
import { resourceProfileLabel, scheduleTimezoneLabel } from "./utils";

const scheduleLabel = (script: Script) => {
  if (!script.scheduleEnabled) {
    return "Manual";
  }

  if (script.scheduleType === "cron") {
    return script.scheduleCron
      ? `Cron: ${script.scheduleCron} (${scheduleTimezoneLabel(script.scheduleTimezone)})`
      : `Cron (${scheduleTimezoneLabel(script.scheduleTimezone)})`;
  }

  if (script.scheduleType === "hourly") {
    return `Hourly at minute ${script.scheduleMinute} (${scheduleTimezoneLabel(script.scheduleTimezone)})`;
  }

  return script.scheduleType;
};

const sourceLabel = (script: Script) =>
  script.executionType === "command" ? "Command" : "GitHub File Path";

export const RoleList = ({ roles }: { roles: string[] }) => {
  if (roles) {
    return (
      <ul>
        {roles.map((role) => (
          <li key={role}>{role}</li>
        ))}
      </ul>
    );
  } else {
    return "<no roles>";
  }
};

const EnvVarList = ({ envVars }: { envVars?: Record<string, string> }) => {
  const entries = Object.entries(envVars ?? {});

  if (entries.length === 0) {
    return <Text>No environment variables.</Text>;
  }

  return (
    <div className="max-h-64 overflow-y-auto rounded border border-gray-300">
      <div className="sticky top-0 grid grid-cols-[minmax(10rem,1fr)_minmax(12rem,1.5fr)] gap-2 border-b border-gray-300 bg-gray-100 px-2 py-1 text-sm font-semibold">
        <span>Key</span>
        <span>Value</span>
      </div>
      <ul className="divide-y divide-gray-200">
        {entries.map(([key, value]) => (
          <li
            className="grid grid-cols-[minmax(10rem,1fr)_minmax(12rem,1.5fr)] gap-2 px-2 py-2"
            key={key}
          >
            <span className="font-mono text-sm">{key}</span>
            <span className="break-all font-mono text-sm">{value}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

interface ScriptViewProps {
  script?: Script;
  onEdit: () => void;
}

export const ScriptView = ({ script, onEdit }: ScriptViewProps) => {
  if (script) {
    return (
      <div className="flex flex-col gap-y-6">
        <div className="flex flex-col gap-2">
          <ViewField label="Id">{script.id}</ViewField>
          <ViewField label="Name">{script.name}</ViewField>
          <ViewField label="Slug">{script.slug}</ViewField>
          <ViewField label="Description">{script.description}</ViewField>
          <ViewField label="Source">{sourceLabel(script)}</ViewField>
          <ViewField label={sourceLabel(script)}>{script.repoPath}</ViewField>
          <ViewField label="Runtime">{script.runtime}</ViewField>
          <ViewField label="Resource Profile">
            {resourceProfileLabel(script.resourceProfile)}
          </ViewField>
          <ViewField label="Timeout">{script.timeoutMinutes} minutes</ViewField>
          <ViewField label="Command Args">
            <RoleList roles={script.commandArgs ?? []} />
          </ViewField>
          <ViewField label="Schedule">
            {scheduleLabel(script)}
          </ViewField>
          <ViewField label="Environment Variables">
            <EnvVarList envVars={script.envVars} />
          </ViewField>
          <ViewField label="Secret Names">
            <RoleList roles={script.secretEnvNames ?? []} />
          </ViewField>
          <ViewField label="Roles">
            <RoleList roles={script.roles ?? []} />
          </ViewField>
          <ViewField label="Active">
            {script.active ? "true" : "false"}
          </ViewField>
          <ViewField label="Created At">
            {dayjs(script.createdTime).toString()}
          </ViewField>
          <ViewField label="Last Update">
            {dayjs(script.updatedTime).toString()}
          </ViewField>
        </div>
        <div className="w-full flex justify-end">
          <Button onClick={onEdit}>Edit</Button>
        </div>
      </div>
    );
  } else {
    return (
      <div className="flex min-h-28 items-center justify-center rounded bg-white text-gray-600">
        <Text>No script has been selected.</Text>
      </div>
    );
  }
};
