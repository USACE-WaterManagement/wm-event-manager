import { AiOutlineLoading } from "react-icons/ai";

const LoadingSpinner = () => (
  <div className="inline-flex items-center gap-2">
    <AiOutlineLoading className="animate-spin text-xl" />
  </div>
);

export default LoadingSpinner;