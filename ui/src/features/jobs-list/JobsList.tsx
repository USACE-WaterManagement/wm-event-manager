import { useAuth } from "@usace-watermanagement/groundwork-water";
import { Accordion, Button } from "@usace/groundwork";
import useJobsList from "./useJobsList";
import { Link } from "@tanstack/react-router";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import JobDetail from "./JobDetail";
import useAdminOffices from "../scripts-manager/useAdminOffices";
import { Dropdown } from "@usace/groundwork";
import { useState } from "react";

dayjs.extend(relativeTime);

const JobsList = () => {
  const auth = useAuth();
  const [office, setOffice] = useState("");
  const adminOffices = useAdminOffices();
  const { data: jobs, isLoading, isError } = useJobsList(office || undefined);

  if (!auth.isAuth) return <span>Login required to view job details.</span>;

  if (isError) return <span>Error occurred while fetching jobs list.</span>;

  if (isLoading) return <span>Loading jobs list...</span>;

  const officeFilter =
    adminOffices.data && adminOffices.data.length > 0 ? (
      <div className="mb-4 flex justify-end">
        <Dropdown
          className="w-48"
          label="Office"
          value={office}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
            setOffice(e.target.value)
          }
          options={[
            <option key="" value="">
              All accessible jobs
            </option>,
            ...adminOffices.data.sort().map((code) => (
              <option key={code} value={code}>
                {code}
              </option>
            )),
          ]}
        />
      </div>
    ) : null;

  if (!jobs || jobs.length <= 0)
    return (
      <div className="mx-auto xl:w-1/2">
        {officeFilter}
        <span>
          No jobs found! You can submit a job{" "}
          <span className="underline">
            <Link to="/submit">here</Link>
          </span>
          .
        </span>
      </div>
    );

  return (
    <div className="mx-auto xl:w-1/2">
      {officeFilter}
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
