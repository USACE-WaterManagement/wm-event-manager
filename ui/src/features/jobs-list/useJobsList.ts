import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@usace-watermanagement/groundwork-water";
import fetchWithAuth from "../../utils/fetchWithAuth";
import { JobDetails } from "./useJobDetails";

const useJobsList = (office?: string) => {
  const auth = useAuth();

  return useQuery({
    queryKey: ["jobs", office ?? ""],
    queryFn: () => fetchJobs(auth.token, office),
    enabled: auth.isAuth,
  });
};

const fetchJobs = async (
  token?: string,
  office?: string,
): Promise<JobDetails[]> => {
  const query = office ? `?office=${encodeURIComponent(office)}` : "";
  const response = await fetchWithAuth(`/api/jobs${query}`, {}, token);
  if (!response.ok) {
    throw new Error("Failed to fetch the jobs list");
  }
  return response.json();
};

export default useJobsList;
