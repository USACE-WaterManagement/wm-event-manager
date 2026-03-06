import { useState } from "react";
import useScriptsCatalog from "./useScriptCatalog";
import { Dropdown } from "@usace/groundwork";
import ScriptExecutor from "./ScriptExecutor";
import { useAuth } from "@usace-watermanagement/groundwork-water";

const ScriptPicker = () => {
  const [office, setOffice] = useState<string | undefined>();
  const [scriptId, setScriptId] = useState<string | undefined>();

  const auth = useAuth();
  const { data, isLoading, isError } = useScriptsCatalog();

  if (!auth.isAuth) return <span>You must log in to execute a script.</span>;
  if (isLoading) return <span>Loading...</span>;
  if (isError || !data) return <span>Error occurred!</span>;

  const scriptsForOffice = data.filter((script) => script.office === office);

  return (
    <div className="flex flex-col">
      <Dropdown
        className="w-36"
        label="Office"
        value={office}
        onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
          setOffice(e.target.value);
          setScriptId(undefined);
        }}
        options={[
          <option key="" value="">
            Office...
          </option>,
          ...Array.from(new Set(data.map((s) => s.office))).map((code) => (
            <option key={code} value={code}>
              {code}
            </option>
          )),
        ]}
      />
      <div className="mt-4">
        <Dropdown
          className="w-96"
          label="Script"
          value={scriptId}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
            setScriptId(e.target.value);
          }}
          options={[
            <option key="" value="">
              Script...
            </option>,
            ...scriptsForOffice.map((script) => (
              <option key={script.id} value={script.id}>
                {script.name}
              </option>
            )),
          ]}
        />
      </div>
      {scriptId && (
        <div className="mt-8">
          <ScriptExecutor scriptId={scriptId} />
        </div>
      )}
    </div>
  );
};

export default ScriptPicker;
