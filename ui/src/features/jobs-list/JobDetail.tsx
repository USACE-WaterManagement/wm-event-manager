import { PropsWithChildren } from "react";
import { JobDetails } from "./useJobDetails";
import { Link } from "@tanstack/react-router";
import { Button } from "@usace/groundwork";

const jobFields: (keyof JobDetails)[] = [
  "Script",
  "User",
  "Status",
  "Office",
  "CreatedTime",
  "JobId",
];

interface JobDetailProps {
  job: JobDetails;
  detailLink?: boolean;
}

function JobDetail({ job, detailLink = false }: JobDetailProps) {
  return (
    <>
      <div className="flex">
        <div className="grow grid grid-cols-2 py-3 px-5">
          {jobFields.map((field) => {
            const className =
              field === "JobId" || field === "CreatedTime"
                ? "col-span-2"
                : "col-span-1";
            return (
              <JobDetailField key={field} field={field} className={className}>
                {job[field]}
              </JobDetailField>
            );
          })}
        </div>
        {detailLink && (
          <Link
            to={`/jobs/$jobId`}
            params={{ jobId: job.JobId }}
            className="px-4 pb-4 content-end"
          >
            <Button>Details</Button>
          </Link>
        )}
      </div>
    </>
  );
}

interface JobDetailFieldProps {
  field: string;
  className?: string;
}

const JobDetailField = ({
  field,
  className,
  children,
}: PropsWithChildren<JobDetailFieldProps>) => (
  <span className={`px-3 py-1.5 ${className}`}>
    <strong>{field}</strong>: {children}
  </span>
);

export default JobDetail;
