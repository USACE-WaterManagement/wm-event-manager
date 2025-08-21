import JobDetail from "./JobDetail";
import JobLogs from "./JobLogs";
import useJobDetails from "./useJobDetails";

interface JobDetailFullProps {
  jobId: string;
}

const JobDetailFull = ({ jobId }: JobDetailFullProps) => {
  const { data, isPending, isError } = useJobDetails(jobId);

  if (isPending) return <span>Loading...</span>;
  if (isError) return <span>Error!</span>;
  if (!data) return null;

  const isFinished = data.Status === "Completed" || data.Status === "Failed";

  return (
    <>
      <JobDetail job={data} />
      <JobLogs jobId={jobId} disabled={!isFinished} />
    </>
  );
};

export default JobDetailFull;
