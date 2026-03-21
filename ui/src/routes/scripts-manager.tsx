import { createFileRoute } from "@tanstack/react-router";
import { ScriptsManager } from "../features/scripts-manager/ScriptsManager";

export const Route = createFileRoute("/scripts-manager")({
  component: ScriptsManager,
});
