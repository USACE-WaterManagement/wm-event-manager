import { PropsWithChildren } from "react";

interface ViewLabelProps {
  children: React.ReactNode;
}

const ViewLabel = ({ children }: ViewLabelProps) => {
  return (
    <span className="select-none font-semibold text-zinc-600 data-disabled:opacity-50 sm:text-sm/6">
      {children}
    </span>
  );
};

interface ViewFieldProps {
  label: string;
}

export const ViewField = ({
  label,
  children,
}: PropsWithChildren<ViewFieldProps>) => {
  return (
    <div className="grid gap-1 border-b border-zinc-200 py-3 last:border-b-0 sm:grid-cols-[150px_minmax(0,1fr)] sm:gap-6">
      <ViewLabel>{label}</ViewLabel>
      <div className="min-w-0 break-words text-zinc-950">{children}</div>
    </div>
  );
};
