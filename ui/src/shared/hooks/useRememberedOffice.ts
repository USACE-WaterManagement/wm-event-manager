import { useEffect, useState } from "react";

const REMEMBERED_OFFICE_KEY = "cwms-batch-events:selected-office";

const loadRememberedOffice = () => {
  if (typeof window === "undefined") return undefined;
  return window.localStorage.getItem(REMEMBERED_OFFICE_KEY) ?? undefined;
};

export const useRememberedOffice = (offices: string[]) => {
  const [office, setOfficeState] = useState<string | undefined>(
    loadRememberedOffice,
  );

  useEffect(() => {
    if (office && offices.length > 0 && !offices.includes(office)) {
      setOfficeState(undefined);
    }
  }, [office, offices]);

  const setOffice = (nextOffice: string) => {
    setOfficeState(nextOffice || undefined);
    if (typeof window === "undefined") return;

    if (nextOffice) {
      window.localStorage.setItem(REMEMBERED_OFFICE_KEY, nextOffice);
    } else {
      window.localStorage.removeItem(REMEMBERED_OFFICE_KEY);
    }
  };

  return [office, setOffice] as const;
};
