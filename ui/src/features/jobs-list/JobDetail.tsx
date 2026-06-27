import { PropsWithChildren } from "react";
import LoadingSpinner from "../../shared/components/LoadingSpinner";
import { JobDetails } from "./useJobDetails";

const jobFields: (keyof JobDetails)[] = [
  "scriptName",
  "username",
  "jobStatus",
  "office",
  "runtime",
  "resourceProfile",
  "timeoutMinutes",
  "createdTime",
  "runTime",
  "endTime",
  "id",
];

const wideFields: (keyof JobDetails)[] = [
  "createdTime",
  "runTime",
  "endTime",
  "id",
];

interface JobDetailProps {
  job: JobDetails;
}

const renderFieldValue = (value: JobDetails[keyof JobDetails]) => {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") return JSON.stringify(value);
  return value;
};

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
              {field === "jobStatus" ? (
                job.jobStatus !== "Completed" && job.jobStatus !== "Failed" ? (
                  <span className="inline-flex items-center gap-2">
                    <span>{job.jobStatus}</span>
                    <LoadingSpinner />
                  </span>
                ) : (
                  job.jobStatus
                )
              ) : (
                renderFieldValue(job[field])
              )}
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
