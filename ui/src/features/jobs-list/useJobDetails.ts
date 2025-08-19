import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@usace-watermanagement/groundwork-water";
import fetchWithAuth from "../../utils/fetchWithAuth";

export interface JobDetails {
  JobId: string;
  Script: string;
  User: string;
  Office: string;
  CreatedTime: string;
  Status: string;
}

const useJobDetails = (jobId: string) => {
  const auth = useAuth();

  return useQuery({
    queryKey: ["job", jobId],
    queryFn: () => fetchJob(jobId, auth.token),
  });
};

const fetchJob = async (jobId: string, token?: string): Promise<JobDetails> => {
  const response = await fetchWithAuth(
    `http://localhost:8000/jobs/${jobId}`,
    {},
    token
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch job ${jobId}`);
  }
  return response.json();
};

export default useJobDetails;
