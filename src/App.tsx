import { SiteWrapper, Container } from "@usace/groundwork";
import "@usace/groundwork/dist/style.css";
import AdHocScriptsPage from "./pages/AdHocScriptsPage";

function App() {
  return (
    <SiteWrapper>
      <Container>
        <AdHocScriptsPage />
      </Container>
    </SiteWrapper>
  );
}

export default App;
