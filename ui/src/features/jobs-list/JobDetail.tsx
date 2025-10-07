import { PropsWithChildren } from "react";
import { JobDetails } from "./useJobDetails";

const jobFields: (keyof JobDetails)[] = [
  "script",
  "user",
  "status",
  "office",
  "createdTime",
  "runTime",
  "endTime",
  "jobId",
];

const wideFields: (keyof JobDetails)[] = [
  "createdTime",
  "runTime",
  "endTime",
  "jobId",
];

interface JobDetailProps {
  job: JobDetails;
}

function JobDetail({ job }: JobDetailProps) {
  return (
    <>
      <div className="grow grid grid-cols-2 py-3 px-5">
        {jobFields.map((field) => {
          const className = wideFields.includes(field)
            ? "col-span-2"
            : "col-span-1";
          return (
            <JobDetailField key={field} field={field} className={className}>
              {job[field]}
            </JobDetailField>
          );
        })}
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
