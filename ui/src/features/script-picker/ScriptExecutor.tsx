import { Button } from "@usace/groundwork";
import useExecuteScript from "./useExecuteScript";

interface ScriptExecutorProps {
  scriptId: string;
}

const ScriptExecutor = ({ scriptId }: ScriptExecutorProps) => {
  const { mutate, isPending, isError, error } = useExecuteScript();

  const handleExecute = () => {
    mutate({ scriptId });
  };

  return (
    <div>
      <Button onClick={handleExecute} disabled={isPending} className="w-24">
        {isPending ? "Submitting..." : "Execute"}
      </Button>
      {isError && (
        <div className="mt-4">
          <span>
            <p>Script failed. Error: {error.message}</p>
          </span>
        </div>
      )}
    </div>
  );
};

export default ScriptExecutor;
