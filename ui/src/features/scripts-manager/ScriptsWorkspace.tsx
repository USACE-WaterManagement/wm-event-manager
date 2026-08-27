import { ScriptDetailPanel } from "./ScriptDetailPanel";
import { ScriptsList } from "./ScriptsList";
import { ScriptCreate, ScriptFormData, ScriptUpdate } from "./types";
import useOfficeScripts from "./useOfficeScripts";
import { useState } from "react";
import { Button, H2 } from "@usace/groundwork";
import { useUpdateScript } from "./useUpdateScript";
import { useCreateScript } from "./useCreateScript";
import { useDeleteScript } from "./useDeleteScript";
import { useDefaultJobRunner } from "./useDefaultJobRunner";

interface ScriptsWorkspaceProps {
  office: string;
}

export const ScriptsWorkspace = ({ office }: ScriptsWorkspaceProps) => {
  const scripts = useOfficeScripts(office);
  const createScriptMutation = useCreateScript(office);
  const deleteScriptMutation = useDeleteScript(office);
  const defaultJobRunner = useDefaultJobRunner();
  const updateScriptMutation = useUpdateScript(office);

  const [selectedScriptId, setSelectedScriptId] = useState<
    string | undefined
  >();

  const [panelMode, setPanelMode] = useState<"view" | "edit">("view");

  if (scripts.isLoading) return <span>Loading scripts...</span>;
  if (defaultJobRunner.isLoading) return <span>Loading job runner...</span>;
  if (scripts.isError)
    return <span>Error occurred while loading scripts.</span>;
  if (defaultJobRunner.isError || !defaultJobRunner.data)
    return <span>Error occurred while loading the default job runner.</span>;
  if (!scripts.data) return <span>No scripts found!</span>;

  const selectedScript = scripts.data.find(
    (script) => script.id === selectedScriptId,
  );

  const onSelect = (scriptId: string) => {
    setPanelMode("view");
    setSelectedScriptId(scriptId);
  };
  const onNew = () => {
    createScriptMutation.reset();
    deleteScriptMutation.reset();
    updateScriptMutation.reset();
    setPanelMode("edit");
    setSelectedScriptId(undefined);
  };
  const onEdit = () => {
    createScriptMutation.reset();
    deleteScriptMutation.reset();
    updateScriptMutation.reset();
    setPanelMode("edit");
  };
  const onDelete = async (scriptId: string) => {
    await deleteScriptMutation.mutateAsync({ scriptId });
    setSelectedScriptId(undefined);
    setPanelMode("view");
  };
  const onSave = async (data: ScriptFormData) => {
    const jobRunners =
      selectedScript?.jobRunners && selectedScript.jobRunners.length > 0
        ? selectedScript.jobRunners
        : [defaultJobRunner.data.id];

    if (selectedScriptId) {
      const payload: ScriptUpdate = {
        ...data,
        jobRunners,
      };
      await updateScriptMutation.mutateAsync({
        scriptId: selectedScriptId,
        payload: payload,
      });
    } else {
      const payload: ScriptCreate = {
        ...data,
        office: office,
        jobRunners,
      };
      const script = await createScriptMutation.mutateAsync({
        payload: payload,
      });
      setSelectedScriptId(script.id);
    }

    setPanelMode("view");
  };
  const onCancelEdit = () => setPanelMode("view");

  const isPending =
    createScriptMutation.isPending ||
    deleteScriptMutation.isPending ||
    updateScriptMutation.isPending;

  const mutationError =
    createScriptMutation.error ||
    deleteScriptMutation.error ||
    updateScriptMutation.error;

  const selectorHeightClass =
    selectedScript || panelMode === "edit"
      ? "min-h-40 max-h-[20vh]"
      : "min-h-64 max-h-[45vh]";

  return (
    <div className="mt-4 flex w-full flex-col gap-5">
      <div className="min-w-0">
        <header className="mb-2 flex items-center justify-between gap-3">
          <H2>{office.toUpperCase()} Scripts</H2>
          <Button onClick={onNew}>New +</Button>
        </header>
        <div className={`${selectorHeightClass} overflow-y-auto`}>
          <ScriptsList
            scripts={scripts.data}
            selectScript={onSelect}
            selectedScriptId={selectedScriptId}
          />
        </div>
      </div>
      <ScriptDetailPanel
        script={selectedScript}
        mode={panelMode}
        isPending={isPending}
        mutationError={mutationError}
        onDelete={onDelete}
        onEdit={onEdit}
        onSave={onSave}
        onCancelEdit={onCancelEdit}
      />
    </div>
  );
};
