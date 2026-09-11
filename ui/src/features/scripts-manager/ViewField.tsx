import { PropsWithChildren } from "react";

interface ViewLabelProps {
  children: React.ReactNode;
}

const ViewLabel = ({ children }: ViewLabelProps) => {
  return (
    <span className="select-none text-base/6 text-zinc-950 data-disabled:opacity-50 sm:text-sm/6">
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
    <div className="grid min-w-0 grid-cols-[120px_minmax(0,1fr)] gap-6">
      <ViewLabel>{label}</ViewLabel>
      <div className="min-w-0">{children}</div>
    </div>
  );
};
