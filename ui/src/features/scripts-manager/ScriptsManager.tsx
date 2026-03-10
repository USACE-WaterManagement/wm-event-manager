import { useAuth } from "@usace-watermanagement/groundwork-water";
import useAdminOffices from "./useAdminOffices";
import { useState } from "react";
import { OfficeSelector } from "../../shared/components/OfficeSelector";
import { ScriptsWorkspace } from "./ScriptsWorkspace";

export const ScriptsManager = () => {
  const auth = useAuth();
  const { data, isLoading, isError } = useAdminOffices();

  const [office, setOffice] = useState<string | undefined>();

  if (!auth.isAuth) return <span>Login required to manage scripts.</span>;

  if (isLoading) return <span>Admin office list is loading...</span>;
  if (isError) return <span>Error fetching admin office list for user</span>;
  if (!data || data.length < 1)
    return <span>You do not have script admin rights for any offices.</span>;

  const officeChange = (office: string) => {
    setOffice(office);
  };

  return (
    <>
      <OfficeSelector offices={data} value={office} onChange={officeChange} />
      {office && <ScriptsWorkspace office={office} />}
    </>
  );
};
