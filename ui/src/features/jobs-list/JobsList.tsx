import { useAuth } from "@usace-watermanagement/groundwork-water";
import { Accordion, Button } from "@usace/groundwork";
import useJobsList from "./useJobsList";
import { Link } from "@tanstack/react-router";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import JobDetail from "./JobDetail";
import LoginPrompt from "../auth/LoginPrompt";

dayjs.extend(relativeTime);

const JobsList = () => {
  const auth = useAuth();
  const { data: jobs, isLoading, isError } = useJobsList();

  if (!auth.isAuth) {
    return (
      <LoginPrompt
        title="Sign in to view jobs"
        description="Review the jobs you submitted, including their current status and output."
      />
    );
  }

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
        const dateAgo = dayjs(job.createdTime).fromNow();
        return (
          <Accordion
            key={job.id}
            heading={
              <span className="flex justify-between w-full gap-1">
                <span>
                  {job.scriptName} ({dateAgo})
                </span>
                <span>{job.jobStatus}</span>
              </span>
            }
          >
            <div className="flex">
              <JobDetail job={job} />
              <Link
                to={`/jobs/$jobId`}
                params={{ jobId: job.id }}
                className="px-4 pb-4 content-end"
              >
                <Button>Details</Button>
              </Link>
            </div>
          </Accordion>
        );
      })}
    </div>
  );
};

export default JobsList;
