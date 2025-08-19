import { createFileRoute } from "@tanstack/react-router";
import JobDetailHandler from "../../features/jobs-list/JobDetailHandler";

export const Route = createFileRoute("/jobs/$jobId")({
  component: JobDetailPage,
});

function JobDetailPage() {
  const { jobId } = Route.useParams();

  return <JobDetailHandler jobId={jobId} />;
}
