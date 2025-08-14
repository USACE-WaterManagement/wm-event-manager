import { useAuth } from "@usace-watermanagement/groundwork-water";
import { Accordion } from "@usace/groundwork";
import useJobsList, { JobDetails } from "./useJobsList";
import { Link } from "@tanstack/react-router";
import { PropsWithChildren } from "react";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";

dayjs.extend(relativeTime);

const jobFields: (keyof JobDetails)[] = [
  "Script",
  "User",
  "Status",
  "Office",
  "CreatedTime",
  "JobId",
];

const JobsList = () => {
  const auth = useAuth();
  const { data: jobs, isLoading, isError } = useJobsList();

  if (!auth.isAuth) return <span>Login required to view job details.</span>;

  if (isError) return <span>Error occurred while fetching jobs list.</span>;

  if (isLoading) return <span>Loading jobs list...</span>;

  if (!jobs || jobs.length <= 0)
    return (
      <span>
        No jobs found! You can submit a job{" "}
        <span className="underline">
          <Link to="/submit">here</Link>
        </span>
        .
      </span>
    );

  return (
    <div className="mx-auto xl:w-1/2">
      {jobs.map((job) => {
        const dateAgo = dayjs(job.CreatedTime).fromNow();
        return (
          <Accordion
            key={job.JobId}
            heading={
              <span className="flex justify-between w-full gap-1">
                <span>
                  {job.Script} ({dateAgo})
                </span>
                <span>{job.Status}</span>
              </span>
            }
          >
            <div className="grid grid-cols-2 py-3 px-5">
              {jobFields.map((field) => {
                const className =
                  field === "JobId" || field === "CreatedTime"
                    ? "col-span-2"
                    : "col-span-1";
                return (
                  <JobDetail key={field} field={field} className={className}>
                    {job[field]}
                  </JobDetail>
                );
              })}
            </div>
          </Accordion>
        );
      })}
    </div>
  );
};

interface JobDetailProps {
  field: string;
  className?: string;
}

const JobDetail = ({
  field,
  className,
  children,
}: PropsWithChildren<JobDetailProps>) => (
  <span className={`px-3 py-1.5 ${className}`}>
    <strong>{field}</strong>: {children}
  </span>
);

export default JobsList;
