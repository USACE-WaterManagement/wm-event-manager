import {
  Table,
  TableBody,
  TableRow,
  TableHead,
  TableHeader,
  TableCell,
} from "@usace/groundwork";
import { FaCircleCheck, FaCircleXmark } from "react-icons/fa6";
import type { Script } from "../scripts-manager/types";

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
    return script.scheduleCron ?? "Cron";
  }

  if (script.scheduleType === "hourly") {
    return `:${String(script.scheduleMinute ?? 0).padStart(2, "0")} hourly`;
  }

  return script.scheduleType;
};

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
    <Table>
      <TableHead>
        <TableRow>
          <TableHeader>Name</TableHeader>
          <TableHeader>Runtime</TableHeader>
          <TableHeader>Size</TableHeader>
          <TableHeader>Schedule</TableHeader>
          <TableHeader>Path</TableHeader>
          <TableHeader>Active</TableHeader>
        </TableRow>
      </TableHead>
      <TableBody>
        {scripts
          .sort((a, b) => a.name.localeCompare(b.name))
          .map((script) => (
            <TableRow
              key={script.id}
              className={
                script.id === selectedScriptId
                  ? "bg-blue-100"
                  : "hover:bg-gray-100"
              }
            >
              <TableCell>
                <button
                  className="block w-full text-left"
                  onClick={() => selectScript(script.id)}
                >
                  <span className="font-bold">{script.name}</span>
                </button>
              </TableCell>
              <TableCell>{script.runtime}</TableCell>
              <TableCell>{script.resourceProfile}</TableCell>
              <TableCell>{scheduleLabel(script)}</TableCell>
              <TableCell>{script.repoPath}</TableCell>
              <TableCell>
                <ActiveIcon isActive={script.active} />
              </TableCell>
            </TableRow>
          ))}
      </TableBody>
    </Table>
  );
};
