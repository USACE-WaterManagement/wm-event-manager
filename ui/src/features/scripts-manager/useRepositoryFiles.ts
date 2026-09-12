import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@usace-watermanagement/groundwork-water";
import fetchWithAuth from "../../utils/fetchWithAuth";

interface Catalog { repository: string; ref: string; paths: string[] }

export function useRepositoryFiles(office: string, enabled = true) {
  const auth = useAuth();
  return useQuery<Catalog>({
    queryKey: ["repository-files", office],
    queryFn: async () => {
      const response = await fetchWithAuth(`/api/repository-files?office=${encodeURIComponent(office)}`, {}, auth.token);
      if (!response.ok) throw new Error("Repository files unavailable");
      return response.json();
    },
    enabled: enabled && auth.isAuth && Boolean(office),
    staleTime: 60_000,
  });
}
