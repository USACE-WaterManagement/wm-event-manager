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

const useJobsList = () => {
  const auth = useAuth();

  return useQuery({
    queryKey: ["jobs"],
    queryFn: () => fetchJobs(auth.token),
  });
};

const fetchJobs = async (token?: string): Promise<JobDetails[]> => {
  const response = await fetchWithAuth("http://localhost:8000/jobs", {}, token);
  if (!response.ok) {
    throw new Error("Failed to fetch the jobs list");
  }
  return response.json();
};

export default useJobsList;
