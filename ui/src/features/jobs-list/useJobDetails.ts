import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@usace-watermanagement/groundwork-water";
import fetchWithAuth from "../../utils/fetchWithAuth";
import { components } from "../../generated/api-types";

export type JobDetails = components["schemas"]["JobRecord"];

const useJobDetails = (jobId: string) => {
  const auth = useAuth();

  return useQuery({
    queryKey: ["job", jobId],
    queryFn: () => fetchJob(jobId, auth.token),
    refetchInterval: (query) => {
      const data = query.state.data;
      if (
        data &&
        (data.jobStatus === "Completed" || data.jobStatus === "Failed")
      )
        return false;
      return 5000;
    },
  });
};

const fetchJob = async (jobId: string, token?: string): Promise<JobDetails> => {
  const response = await fetchWithAuth(`/api/jobs/${jobId}`, {}, token);
  if (!response.ok) {
    throw new Error(`Failed to fetch job ${jobId}`);
  }
  return response.json();
};

export default useJobDetails;
