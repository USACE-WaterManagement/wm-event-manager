import { createFileRoute } from "@tanstack/react-router";
import ScriptPicker from "../features/script-picker/ScriptPicker";

export const Route = createFileRoute("/")({
  component: ScriptPicker,
});
