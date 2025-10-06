import { useMutation } from "@tanstack/react-query";
import fetchWithAuth from "../../utils/fetchWithAuth";
import { useAuth } from "@usace-watermanagement/groundwork-water";
import { JobDetails } from "../jobs-list/useJobDetails";
import { useNavigate } from "@tanstack/react-router";
import { components } from "../../generated/api-types";

export type ExecuteScriptPayload = components["schemas"]["ScriptRunRequest"];

const useExecuteScript = () => {
  const auth = useAuth();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (payload: ExecuteScriptPayload) =>
      executeScript(payload, auth.token),
    onSuccess: (job: JobDetails) => {
      navigate({ to: "/jobs/$jobId", params: { jobId: job.jobId } });
    },
  });
};

const executeScript = async (
  payload: ExecuteScriptPayload,
  token?: string
): Promise<JobDetails> => {
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
