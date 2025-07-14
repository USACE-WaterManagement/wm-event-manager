import { useQuery } from "@tanstack/react-query";

interface ScriptsCatalog {
  [office: string]: { scripts: string[] };
}

const useScriptsCatalog = () => {
  return useQuery({
    queryKey: ["catalog"],
    queryFn: fetchCatalog,
  });
};

const fetchCatalog = async (): Promise<ScriptsCatalog> => {
  const response = await fetch("http://localhost:8000/scripts/catalog");
  if (!response.ok) {
    throw new Error("Failed to fetch the scripts catalog");
  }
  return response.json();
};

export default useScriptsCatalog;
