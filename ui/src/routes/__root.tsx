import { createRootRoute, Outlet } from "@tanstack/react-router";
import { SiteWrapper, Container } from "@usace/groundwork";
import "@usace/groundwork/dist/style.css";
import AuthButton from "../features/auth/AuthButton";

const navLinks = [
  { id: "jobs", text: "Jobs List", href: "/jobs" },
  { id: "submit", text: "Submit Job", href: "/submit" },
];

export const Route = createRootRoute({
  component: RootComponent,
});

function RootComponent() {
  return (
    <SiteWrapper links={navLinks} navRight={<AuthButton />}>
      <Container>
        <div className="my-6">
          <Outlet />
        </div>
      </Container>
    </SiteWrapper>
  );
}
