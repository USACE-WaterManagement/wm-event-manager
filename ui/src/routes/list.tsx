import { createFileRoute } from "@tanstack/react-router";
import JobsList from "../features/jobs-list/JobsList";

export const Route = createFileRoute("/list")({
  component: JobsList,
});
