import { useMutation } from "@tanstack/react-query";
import fetchWithAuth from "../../utils/fetchWithAuth";
import { useAuth } from "@usace-watermanagement/groundwork-water";

interface ExecuteScriptPayload {
  officeName: string;
  scriptName: string;
}

const useExecuteScript = () => {
  const auth = useAuth();

  return useMutation({
    mutationFn: (payload: ExecuteScriptPayload) =>
      executeScript(payload, auth.token),
  });
};

const executeScript = async (payload: ExecuteScriptPayload, token?: string) => {
  const response = await fetchWithAuth(
    "http://localhost:8000/scripts/execute",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    },
    token
  );

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
};

export default useExecuteScript;
