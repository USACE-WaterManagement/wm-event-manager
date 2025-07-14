import { useMutation } from "@tanstack/react-query";

interface ExecuteScriptPayload {
  officeName: string;
  scriptName: string;
}

const useExecuteScript = () => {
  return useMutation({
    mutationFn: executeScript,
  });
};

const executeScript = async (payload: ExecuteScriptPayload) => {
  const response = await fetch("http://localhost:8000/scripts/execute", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
};

export default useExecuteScript;
