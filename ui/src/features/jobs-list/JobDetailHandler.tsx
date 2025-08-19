import JobDetail from "./JobDetail";
import useJobDetails from "./useJobDetails";

interface JobDetailHandlerProps {
  jobId: string;
}

const JobDetailHandler = ({ jobId }: JobDetailHandlerProps) => {
  const { data, isPending, isError } = useJobDetails(jobId);

  if (isPending) return <span>Loading...</span>;
  if (isError) return <span>Error!</span>;
  if (!data) return null;
  return <JobDetail job={data} />;
};

export default JobDetailHandler;
