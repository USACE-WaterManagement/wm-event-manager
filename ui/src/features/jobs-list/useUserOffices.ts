import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@usace-watermanagement/groundwork-water";
import fetchWithAuth from "../../utils/fetchWithAuth";

const useUserOffices = () => {
  const auth = useAuth();

  return useQuery({
    queryKey: ["userOffices"],
    queryFn: () => fetchUserOffices(auth.token),
    enabled: auth.isAuth,
  });
};

const fetchUserOffices = async (token?: string): Promise<string[]> => {
  const response = await fetchWithAuth("/api/users/me/offices", {}, token);
  if (!response.ok) {
    throw new Error("Failed to fetch offices for user");
  }
  return response.json();
};

export default useUserOffices;
