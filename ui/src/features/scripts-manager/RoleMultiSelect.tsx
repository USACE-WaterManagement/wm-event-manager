import { useState } from "react";
import { Dropdown } from "@usace/groundwork";
import { TiDelete } from "react-icons/ti";

type RoleMultiSelectProps = {
  allRoles: string[];
  initialSelectedRoles?: string[];
  onChange?: (selectedRoles: string[]) => void;
};

export const RoleMultiSelect = ({
  allRoles,
  initialSelectedRoles = [],
  onChange,
}: RoleMultiSelectProps) => {
  const [selectedRoles, setSelectedRoles] =
    useState<string[]>(initialSelectedRoles);

  const addRole = (addedRole: string) => {
    if (!selectedRoles.includes(addedRole)) {
      const updated = [...selectedRoles, addedRole];
      setSelectedRoles(updated);
      onChange?.(updated);
    }
  };

  const removeRole = (removedRole: string) => {
    const updated = selectedRoles.filter((role) => role !== removedRole);
    setSelectedRoles(updated);
    onChange?.(updated);
  };

  const availableRoles = allRoles.filter((r) => !selectedRoles.includes(r));

  return (
    <div>
      <div className="flex flex-col">
        {selectedRoles.map((role) => {
          return (
            <div key={role} className="flex">
              <span style={{ marginRight: "4px" }}>{role}</span>
              <button
                type="button"
                onClick={() => removeRole(role)}
                className="cursor-pointer"
              >
                <TiDelete />
              </button>
            </div>
          );
        })}
      </div>

      {availableRoles.length > 0 && (
        <Dropdown
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
            if (e.target.value) {
              addRole(e.target.value);
              e.target.value = "";
            }
          }}
          options={[
            <option key="placeholder" value="">
              + Add role...
            </option>,
            ...availableRoles.map((role) => (
              <option key={role} value={role}>
                {role}
              </option>
            )),
          ]}
        />
      )}
    </div>
  );
};
