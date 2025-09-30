import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@usace-watermanagement/groundwork-water";
import fetchWithAuth from "../../utils/fetchWithAuth";

export interface JobDetails {
  jobId: string;
  script: string;
  user: string;
  office: string;
  createdTime: string;
  status: string;
}

const useJobDetails = (jobId: string) => {
  const auth = useAuth();

  return useQuery({
    queryKey: ["job", jobId],
    queryFn: () => fetchJob(jobId, auth.token),
    refetchInterval: (query) => {
      const data = query.state.data;
      console.log(data);
      if (data && (data.status === "Completed" || data.status === "Failed"))
        return false;
      return 5000;
    },
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
