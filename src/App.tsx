import { SiteWrapper, Container, UsaceBox } from "@usace/groundwork";
import "@usace/groundwork/dist/style.css";

function App() {
  return (
    <SiteWrapper>
      <Container>
        <UsaceBox title="My New Site">
          <div>Hello World</div>
        </UsaceBox>
      </Container>
    </SiteWrapper>
  );
}

export default App;
