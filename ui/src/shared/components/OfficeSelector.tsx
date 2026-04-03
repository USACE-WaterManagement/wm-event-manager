import { Dropdown } from "@usace/groundwork";

interface OfficeSelectorProps {
  offices: string[];
  value?: string;
  onChange: (office: string) => void;
}

export const OfficeSelector = ({
  offices,
  value,
  onChange,
}: OfficeSelectorProps) => {
  return (
    <Dropdown
      className="w-36"
      label="Office"
      value={value}
      onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
        onChange(e.target.value);
      }}
      options={[
        <option key="" value="">
          Office...
        </option>,
        ...offices.sort().map((code) => (
          <option key={code} value={code}>
            {code}
          </option>
        )),
      ]}
    />
  );
};
