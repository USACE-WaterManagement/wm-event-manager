import { useState } from "react";
import useScriptsCatalog from "./useScriptCatalog";
import { Dropdown } from "@usace/groundwork";

const OFFICE_PLACEHOLDER = "Office...";
const SCRIPT_PLACEHOLDER = "Script...";

const ScriptPicker = () => {
  const [office, setOffice] = useState(OFFICE_PLACEHOLDER);
  const [script, setScript] = useState(SCRIPT_PLACEHOLDER);

  const { data, isLoading, isError } = useScriptsCatalog();

  if (isLoading) return <span>Loading...</span>;

  if (isError || !data) return <span>Error occurred!</span>;

  const officeOptions = [OFFICE_PLACEHOLDER, ...Object.keys(data)];
  const scriptOptions = [SCRIPT_PLACEHOLDER];
  if (data?.[office]?.scripts.length > 0)
    scriptOptions.push(...data[office].scripts);

  return (
    <div className="flex flex-col">
      <Dropdown
        className="w-36"
        label="Office"
        value={office}
        onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
          setOffice(e.target.value);
          setScript(SCRIPT_PLACEHOLDER);
        }}
        options={officeOptions.map((code) => (
          <option key={code} value={code}>
            {code}
          </option>
        ))}
      />
      <div className="mt-4">
        <Dropdown
          className="w-96"
          label="Script"
          value={script}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
            setScript(e.target.value);
          }}
          options={scriptOptions.map((script) => (
            <option key={script} value={script}>
              {script}
            </option>
          ))}
        />
      </div>
    </div>
  );
};

export default ScriptPicker;
