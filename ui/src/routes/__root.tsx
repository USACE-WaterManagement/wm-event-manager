import { createRootRoute, Outlet } from "@tanstack/react-router";
import { SiteWrapper, Container } from "@usace/groundwork";
import "@usace/groundwork/dist/groundwork.css";
import AuthButton from "../features/auth/AuthButton";

const apiUrl = (path: string) =>
  new URL(`/api/${path}`, window.location.origin).href;

const navLinks = [
  { id: "jobs", text: "Jobs List", href: "/jobs" },
  { id: "submit", text: "Submit Job", href: "/submit" },
  { id: "manager", text: "Scripts Manager", href: "/scripts-manager" },
  { id: "setup", text: "Email templates", href: "/setup" },
  {
    id: "developer",
    text: "Developer",
    href: "#",
    children: [
      {
        id: "swagger",
        text: "Swagger API Explorer",
        href: apiUrl("docs"),
        target: "_blank",
        rel: "noreferrer",
      },
      {
        id: "redoc",
        text: "ReDoc API Reference",
        href: apiUrl("redoc"),
        target: "_blank",
        rel: "noreferrer",
      },
      {
        id: "openapi",
        text: "OpenAPI Schema",
        href: apiUrl("openapi.json"),
        target: "_blank",
        rel: "noreferrer",
      },
    ],
  },
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
