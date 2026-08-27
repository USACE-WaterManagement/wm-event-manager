import { useAuth } from "@usace-watermanagement/groundwork-water";
import { Button } from "@usace/groundwork";
import { FiLogIn, FiLogOut } from "react-icons/fi";

const AuthButton = () => {
  const auth = useAuth();

  return (
    <Button
      color="white"
      style="plain"
      className="gw-flex gw-items-center gw-gap-2 gw-font-normal"
      onClick={auth.isAuth ? auth.logout : auth.login}
    >
      {auth.isAuth ? <FiLogOut aria-hidden="true" /> : <FiLogIn aria-hidden="true" />}
      {auth.isAuth ? "Logout" : "Login"}
    </Button>
  );
};

export default AuthButton;
