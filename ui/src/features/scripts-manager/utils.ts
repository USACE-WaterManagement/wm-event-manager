export const allRoles = [
  "All Users",
  "CCP Mgr",
  "CCP Proc",
  "CCP Reviewer",
  "CWMS DBA Users",
  "CWMS PD Users",
  "CWMS User Admins",
  "CWMS Users",
  "Data Acquisition Mgr",
  "Data Exchange Mgr",
  "NWO_Readonly_Users",
  "RDL Mgr",
  "RDL Reviewer",
  "TS ID Creator",
  "VT Mgr",
  "Viewer Users",
];

export const resourceProfileLabels: Record<string, string> = {
  small: "Small - 1 vCPU / 2 GB",
  medium: "Medium - 2 vCPU / 4 GB",
  large: "Large - 4 vCPU / 8 GB",
};

export const resourceProfileLabel = (profile: string) =>
  resourceProfileLabels[profile] ?? profile;

export const defaultScheduleTimezone = "UTC";

const intlWithTimezones = Intl as typeof Intl & {
  supportedValuesOf?: (key: "timeZone") => string[];
};

export const availableScheduleTimezones = Array.from(
  new Set([
    defaultScheduleTimezone,
    ...(intlWithTimezones.supportedValuesOf?.("timeZone") ?? []),
  ]),
).sort((a, b) => a.localeCompare(b));

export const isValidScheduleTimezone = (value?: string | null) =>
  typeof value === "string" &&
  availableScheduleTimezones.includes(value.trim());

export const scheduleTimezoneLabel = (value?: string | null) =>
  isValidScheduleTimezone(value) ? value!.trim() : defaultScheduleTimezone;
