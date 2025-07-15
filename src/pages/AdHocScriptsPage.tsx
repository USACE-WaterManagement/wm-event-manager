import { useAuth } from "@usace-watermanagement/groundwork-water";
import ScriptPicker from "../features/script-picker/ScriptPicker";

const AdHocScriptsPage = () => {
  const auth = useAuth();

  return (
    <div className="my-6">
      {auth.isAuth ? (
        <ScriptPicker />
      ) : (
        <span>Login required to execute scripts.</span>
      )}
    </div>
  );
};

export default AdHocScriptsPage;
