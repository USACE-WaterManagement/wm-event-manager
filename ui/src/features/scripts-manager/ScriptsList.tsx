import { FaCircleCheck, FaCircleXmark } from "react-icons/fa6";
import { MdEdit } from "react-icons/md";
import type { Script } from "../scripts-manager/types";
import { resourceProfileLabel, scheduleTimezoneLabel } from "./utils";

interface ActiveIconProps {
  isActive: boolean;
}

const ActiveIcon = ({ isActive }: ActiveIconProps) => {
  if (isActive) {
    return <FaCircleCheck className="text-green-500" />;
  } else {
    return <FaCircleXmark className="text-red-500" />;
  }
};

const scheduleLabel = (script: Script) => {
  if (!script.scheduleEnabled) {
    return "Manual";
  }

  if (script.scheduleType === "cron") {
    return script.scheduleCron
      ? `${script.scheduleCron} ${scheduleTimezoneLabel(script.scheduleTimezone)}`
      : `Cron ${scheduleTimezoneLabel(script.scheduleTimezone)}`;
  }

  if (script.scheduleType === "hourly") {
    return `:${String(script.scheduleMinute ?? 0).padStart(2, "0")} hourly ${scheduleTimezoneLabel(script.scheduleTimezone)}`;
  }

  return script.scheduleType;
};

const sourceLabel = (script: Script) =>
  script.executionType === "command" ? "Command" : "File";

interface ScriptsListProps {
  scripts: Script[];
  selectScript: (scriptId: string) => void;
  selectedScriptId?: string;
}

export const ScriptsList = ({
  scripts,
  selectScript,
  selectedScriptId,
}: ScriptsListProps) => {
  return (
    <div className="overflow-hidden rounded border border-gray-200">
      <table className="w-full table-fixed text-sm">
        <colgroup>
          <col className="w-[3.5rem]" />
          <col className="w-[30%]" />
          <col className="w-[11%]" />
          <col className="w-[18%]" />
          <col className="w-[17%]" />
          <col className="w-[12%]" />
          <col className="w-[8%]" />
        </colgroup>
        <thead className="sticky top-0 z-10 border-b border-gray-200 bg-gray-100 text-left text-gray-600">
          <tr>
            <th className="px-2 py-2 font-semibold">Edit</th>
            <th className="px-2 py-2 font-semibold">Name</th>
            <th className="px-2 py-2 font-semibold">Runtime</th>
            <th className="px-2 py-2 font-semibold">Size</th>
            <th className="px-2 py-2 font-semibold">Schedule</th>
            <th className="px-2 py-2 font-semibold">Source</th>
            <th className="px-2 py-2 font-semibold">Active</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
        {scripts
          .sort((a, b) => a.name.localeCompare(b.name))
          .map((script) => {
            const rowClasses =
              script.id === selectedScriptId
                ? "cursor-pointer bg-blue-100"
                : "cursor-pointer hover:bg-gray-100";

            return (
              <tr
                key={script.id}
                className={rowClasses}
                role="button"
                tabIndex={0}
                onClick={() => selectScript(script.id)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    selectScript(script.id);
                  }
                }}
              >
              <td className="px-2 py-2 align-middle">
                <button
                  aria-label={`Edit ${script.name}`}
                  className="inline-flex size-9 items-center justify-center rounded border border-gray-300 bg-white text-blue-800 hover:bg-blue-50"
                  title={script.name}
                  type="button"
                  onClick={(event) => {
                    event.stopPropagation();
                    selectScript(script.id);
                  }}
                >
                  <MdEdit className="size-5" />
                </button>
              </td>
              <td className="truncate px-2 py-3 align-middle font-bold" title={script.name}>
                {script.name}
              </td>
              <td className="truncate px-2 py-3 align-middle" title={script.runtime}>
                {script.runtime}
              </td>
              <td
                className="truncate px-2 py-3 align-middle"
                title={resourceProfileLabel(script.resourceProfile)}
              >
                {resourceProfileLabel(script.resourceProfile)}
              </td>
              <td
                className="truncate px-2 py-3 align-middle"
                title={scheduleLabel(script)}
              >
                {scheduleLabel(script)}
              </td>
              <td
                className="truncate px-2 py-3 align-middle"
                title={`${sourceLabel(script)}: ${script.repoPath}`}
              >
                {sourceLabel(script)}
              </td>
              <td className="px-2 py-3 align-middle">
                <ActiveIcon isActive={script.active} />
              </td>
            </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
