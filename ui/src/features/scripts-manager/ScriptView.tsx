import dayjs from "dayjs";
import { ViewField } from "./ViewField";
import { Badge, Button, Card, H3, Text } from "@usace/groundwork";
import type { Script } from "../scripts-manager/types";

export const RoleList = ({ roles }: { roles: string[] }) => {
  if (roles) {
    return (
      <ul className="flex flex-wrap gap-2" aria-label="Allowed roles">
        {roles.map((role) => (
          <li key={role}>
            <Badge color="blue">{role}</Badge>
          </li>
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
      <Card className="mt-4 flex flex-col gap-5 p-5 sm:p-6">
        <header className="flex flex-wrap items-start justify-between gap-4 border-b border-zinc-200 pb-4">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <H3>{script.name}</H3>
              <Badge color={script.active ? "green" : "zinc"}>
                {script.active ? "Active" : "Inactive"}
              </Badge>
            </div>
            <Text className="mt-1 text-zinc-600">
              {script.description || "No description has been provided."}
            </Text>
          </div>
          <Button onClick={onEdit}>Edit script</Button>
        </header>

        <section aria-label="Script configuration">
          <ViewField label="Script ID">
            <code className="text-sm">{script.id}</code>
          </ViewField>
          <ViewField label="Slug">
            <code className="text-sm">{script.slug}</code>
          </ViewField>
          <ViewField label="Repository path">
            <code className="rounded bg-zinc-100 px-2 py-1 text-sm">
              {script.repoPath}
            </code>
          </ViewField>
          <ViewField label="Runtime">
            <Badge color="zinc">{script.executionType}</Badge>
          </ViewField>
          <ViewField label="Roles">
            <RoleList roles={script.roles} />
          </ViewField>
        </section>

        <section
          aria-label="Script history"
          className="grid gap-3 rounded-lg bg-zinc-50 p-4 sm:grid-cols-2"
        >
          <div>
            <Text className="font-semibold text-zinc-600">Created</Text>
            <Text>
              {dayjs(script.createdTime).format("MMM D, YYYY h:mm A")}
            </Text>
          </div>
          <div>
            <Text className="font-semibold text-zinc-600">Last updated</Text>
            <Text>
              {dayjs(script.updatedTime).format("MMM D, YYYY h:mm A")}
            </Text>
          </div>
        </section>
      </Card>
    );
  } else {
    return <Text>No script has been selected.</Text>;
  }
};
