import { Button } from "@usace/groundwork";
import useExecuteScript from "./useExecuteScript";

interface ScriptExecutorProps {
  office: string;
  script: string;
}

const ScriptExecutor = ({ office, script }: ScriptExecutorProps) => {
  const { mutate, isPending, isSuccess, isError, data, error } =
    useExecuteScript();

  const handleExecute = () => {
    mutate({ officeName: office, scriptName: script });
  };

  return (
    <div>
      <Button onClick={handleExecute} disabled={isPending} className="w-24">
        {isPending ? "Running..." : "Execute"}
      </Button>
      <div className="mt-4">
        <span>
          {isSuccess && (
            <>
              <p>Script executed successfully. Result: </p>
              <textarea rows={20} cols={100} value={data} readOnly />
            </>
          )}
        </span>
        <span>{isError && <p>Script failed. Error: {error.message}</p>}</span>
      </div>
    </div>
  );
};

export default ScriptExecutor;
