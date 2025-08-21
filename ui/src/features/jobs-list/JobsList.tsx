import { useAuth } from "@usace-watermanagement/groundwork-water";
import { Accordion } from "@usace/groundwork";
import useJobsList from "./useJobsList";
import { Link } from "@tanstack/react-router";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import JobDetail from "./JobDetail";

dayjs.extend(relativeTime);

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

  console.log({ jobs });

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
            <JobDetail job={job} detailLink />
          </Accordion>
        );
      })}
    </div>
  );
};

export default JobsList;
