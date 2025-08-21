import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@usace-watermanagement/groundwork-water";
import fetchWithAuth from "../../utils/fetchWithAuth";

interface JobLogs {
  logs: string;
}

const useJobLogs = (jobId: string, enabled: boolean) => {
  const auth = useAuth();

  return useQuery({
    queryKey: ["job", jobId, "logs"],
    queryFn: () => fetchJobs(jobId, auth.token),
    enabled,
  });
};

const fetchJobs = async (jobId: string, token?: string): Promise<JobLogs> => {
  const response = await fetchWithAuth(
    `http://localhost:8000/jobs/${jobId}/logs`,
    {},
    token
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch logs for job ${jobId}`);
  }
  return response.json();
};

export default useJobLogs;
