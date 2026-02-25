import { useAuth } from "@usace-watermanagement/groundwork-water";
import { Dropdown } from "@usace/groundwork";
import useAdminOffices from "./useAdminOffices";
import { useState } from "react";

const OFFICE_PLACEHOLDER = "Office...";

export const ScriptsManager = () => {
  const auth = useAuth();
  const { data, isLoading, isError } = useAdminOffices();

  const [office, setOffice] = useState(OFFICE_PLACEHOLDER);

  if (!auth.isAuth) return <span>Login required to manage scripts.</span>;

  if (isLoading) return <span>Admin office list is loading...</span>;
  if (isError) return <span>Error fetching admin office list for user</span>;
  if (!data || data.length < 1)
    return <span>You do not have script admin rights for any offices.</span>;

  return (
    <Dropdown
      className="w-36"
      label="Office"
      value={office}
      onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
        setOffice(e.target.value);
      }}
      options={data.sort().map((code) => (
        <option key={code} value={code}>
          {code}
        </option>
      ))}
    />
  );
};
