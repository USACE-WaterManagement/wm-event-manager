import { ScriptForm } from "./ScriptForm";
import { ScriptView } from "./ScriptView";
import type { Script, ScriptFormData } from "../scripts-manager/types";

interface ScriptDetailPanelProps {
  mode: "view" | "edit";
  script?: Script;
  isPending: boolean;
  mutationError: Error | null;
  onDelete: (scriptId: string) => void;
  onEdit: () => void;
  onSave: (data: ScriptFormData) => void;
  onCancelEdit: () => void;
}

export const ScriptDetailPanel = ({
  mode,
  script,
  isPending,
  mutationError,
  onDelete,
  onEdit,
  onSave,
  onCancelEdit,
}: ScriptDetailPanelProps) => {
  let innerComponent;

  if (mode === "view") {
    innerComponent = <ScriptView script={script} onEdit={onEdit} />;
  } else if (mode === "edit") {
    innerComponent = (
      <ScriptForm
        key={script?.id ?? "new"}
        script={script}
        isPending={isPending}
        mutationError={mutationError}
        onDelete={onDelete}
        onSave={onSave}
        onCancelEdit={onCancelEdit}
      />
    );
  }

  return <div>{innerComponent}</div>;
};
