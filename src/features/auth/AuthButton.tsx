import { useAuth } from "@usace-watermanagement/groundwork-water";
import { LoginButton } from "@usace/groundwork";

const AuthButton = () => {
  const auth = useAuth();

  return auth.isAuth ? (
    <span>Logged in!</span>
  ) : (
    <LoginButton onClick={auth.login} />
  );
};

export default AuthButton;
