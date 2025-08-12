import { createFileRoute } from "@tanstack/react-router";
import AdHocScriptsPage from "../pages/AdHocScriptsPage";

export const Route = createFileRoute("/")({
  component: AdHocScriptsPage,
});
