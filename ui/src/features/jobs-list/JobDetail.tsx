import { PropsWithChildren } from "react";
import { JobDetails } from "./useJobsList";

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
}

function JobDetail({ job }: JobDetailProps) {
  return (
    <div className="grid grid-cols-2 py-3 px-5">
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
