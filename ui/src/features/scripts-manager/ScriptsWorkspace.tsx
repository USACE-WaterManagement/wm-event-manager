import { ScriptDetailPanel } from "./ScriptDetailPanel";
import { ScriptsList } from "./ScriptsList";
import { ScriptCreate, ScriptFormData, ScriptUpdate } from "./types";
import useOfficeScripts from "./useOfficeScripts";
import { useState } from "react";
import { Button, H2 } from "@usace/groundwork";
import { useUpdateScript } from "./useUpdateScript";
import { useCreateScript } from "./useCreateScript";
import { useDeleteScript } from "./useDeleteScript";
import { ScriptNotificationEditor } from "../notifications-manager/ScriptNotificationEditor";

const BATCH_RUNNER_UUID = "58600a09-f18e-42c5-9d3c-df52ebe409f9";

interface ScriptsWorkspaceProps {
  office: string;
}

export const ScriptsWorkspace = ({ office }: ScriptsWorkspaceProps) => {
  const scripts = useOfficeScripts(office);
  const createScriptMutation = useCreateScript(office);
  const deleteScriptMutation = useDeleteScript(office);
  const updateScriptMutation = useUpdateScript(office);

  const [selectedScriptId, setSelectedScriptId] = useState<
    string | undefined
  >();

  const [panelMode, setPanelMode] = useState<"view" | "edit">("view");
  const [selectedTab, setSelectedTab] = useState<"details" | "notify">("details");

  if (scripts.isLoading) return <span>Loading scripts...</span>;
  if (scripts.isError)
    return <span>Error occurred while loading scripts.</span>;
  if (!scripts.data) return <span>No scripts found!</span>;

  const selectedScript = scripts.data.find(
    (script) => script.id === selectedScriptId,
  );

  const onSelect = (scriptId: string) => {
    setPanelMode("view");
    setSelectedTab("details");
    setSelectedScriptId(scriptId);
  };
  const onNew = () => {
    createScriptMutation.reset();
    deleteScriptMutation.reset();
    updateScriptMutation.reset();
    setPanelMode("edit");
    setSelectedTab("details");
    setSelectedScriptId(undefined);
  };
  const onEdit = () => {
    createScriptMutation.reset();
    deleteScriptMutation.reset();
    updateScriptMutation.reset();
    setPanelMode("edit");
    setSelectedTab("details");
  };
  const onDelete = async (scriptId: string) => {
    await deleteScriptMutation.mutateAsync({ scriptId });
    setSelectedScriptId(undefined);
    setPanelMode("view");
  };
  const onSave = async (data: ScriptFormData) => {
    if (selectedScriptId) {
      const payload: ScriptUpdate = {
        ...data,
        executionType: "python",
        jobRunners: [BATCH_RUNNER_UUID],
      };
      await updateScriptMutation.mutateAsync({
        scriptId: selectedScriptId,
        payload: payload,
      });
    } else {
      const payload: ScriptCreate = {
        ...data,
        office: office,
        executionType: "python",
        jobRunners: [BATCH_RUNNER_UUID],
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

  return (
    <>
      <div className="mt-4 grid w-full grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="min-w-0">
          <header className="flex flex-wrap items-center justify-between gap-3">
            <H2>{office.toUpperCase()} Scripts</H2>
            <Button onClick={onNew}>New script</Button>
          </header>
          <ScriptsList
            scripts={scripts.data}
            selectScript={onSelect}
            selectedScriptId={selectedScriptId}
          />
        </div>
        <section className="min-w-0 rounded-lg bg-gray-100 p-4">
          {selectedScript && panelMode === "view" && (
            <div
              className="mb-4 flex gap-2 border-b border-gray-300"
              role="tablist"
              aria-label="Script settings"
            >
              <button
                type="button"
                role="tab"
                aria-selected={selectedTab === "details"}
                className={`px-4 py-2 font-semibold ${
                  selectedTab === "details" ? "bg-white" : "hover:bg-gray-200"
                }`}
                onClick={() => setSelectedTab("details")}
              >
                Details
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={selectedTab === "notify"}
                className={`px-4 py-2 font-semibold ${
                  selectedTab === "notify" ? "bg-white" : "hover:bg-gray-200"
                }`}
                onClick={() => setSelectedTab("notify")}
              >
                Email notification
              </button>
            </div>
          )}
          {selectedScript && selectedTab === "notify" && panelMode === "view" ? (
            <ScriptNotificationEditor script={selectedScript} />
          ) : (
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
          )}
        </section>
      </div>
    </>
  );
};
