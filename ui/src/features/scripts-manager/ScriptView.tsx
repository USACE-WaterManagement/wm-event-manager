import dayjs from "dayjs";
import { ViewField } from "./ViewField";
import { Button, Text } from "@usace/groundwork";
import type { Script } from "../scripts-manager/types";

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
          <ViewField label="GitHub Repo Path">{script.repoPath}</ViewField>
          <ViewField label="Execution Type">{script.executionType}</ViewField>
          <ViewField label="Runtime">{script.runtime}</ViewField>
          <ViewField label="Resource Profile">{script.resourceProfile}</ViewField>
          <ViewField label="Environment Variables">
            <pre className="whitespace-pre-wrap">
              {JSON.stringify(script.envVars ?? {}, null, 2)}
            </pre>
          </ViewField>
          <ViewField label="Secret Names">
            <RoleList roles={script.secretEnvNames ?? []} />
          </ViewField>
          <ViewField label="Roles">
            <RoleList roles={script.roles} />
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
    return <Text>No script has been selected.</Text>;
  }
};
