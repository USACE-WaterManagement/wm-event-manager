import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@usace-watermanagement/groundwork-water";
import fetchWithAuth from "../../utils/fetchWithAuth";

interface ScriptsCatalog {
  [office: string]: { scripts: string[] };
}

const useScriptsCatalog = () => {
  const auth = useAuth();

  return useQuery({
    queryKey: ["catalog"],
    queryFn: () => fetchCatalog(auth.token),
  });
};

const fetchCatalog = async (token?: string): Promise<ScriptsCatalog> => {
  const response = await fetchWithAuth(
    "http://localhost:8000/scripts/catalog",
    {},
    token
  );
  if (!response.ok) {
    throw new Error("Failed to fetch the scripts catalog");
  }
  return response.json();
};

export default useScriptsCatalog;
