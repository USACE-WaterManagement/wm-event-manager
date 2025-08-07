import { SiteWrapper, Container } from "@usace/groundwork";
import "@usace/groundwork/dist/style.css";
import AdHocScriptsPage from "./pages/AdHocScriptsPage";
import AuthButton from "./features/auth/AuthButton";

function App() {
  return (
    <SiteWrapper navRight={<AuthButton />}>
      <Container>
        <AdHocScriptsPage />
      </Container>
    </SiteWrapper>
  );
}

export default App;
