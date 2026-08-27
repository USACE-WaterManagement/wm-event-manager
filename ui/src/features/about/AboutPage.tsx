import type { CSSProperties, ReactNode } from "react";
import { useAuth } from "@usace-watermanagement/groundwork-water";
import {
  Card, H1, H2, H3, Table, TableBody, TableCell, TableHead, TableHeader,
  TableRow, Tabs, Text,
} from "@usace/groundwork";
import LoadingSpinner from "../../shared/components/LoadingSpinner";
import { type ApplicationInfo, useApplicationInfo, useSchemaInfo } from "./useAboutInfo";

const uiVersion = import.meta.env.VITE_UI_VERSION || "local";
const uiBuildTime = import.meta.env.VITE_UI_BUILD_TIME;
const github = {
  application: "https://github.com/USACE-WaterManagement/cwms-batch-events",
  cda: "https://github.com/USACE/cwms-data-api",
  lrhJobs: "https://github.com/USACE-WaterManagement/lrh-wm-cwbi-jobs",
  swtJobs: "https://github.com/USACE-WaterManagement/swt-wm-cwbi-jobs",
};

const formatDate = (value?: string) =>
  value
    ? new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(value))
    : "Local development build";

const Detail = ({ label, value }: { label: string; value: string }) => (
  <div className="border-b border-slate-200 py-3 last:border-0 sm:grid sm:grid-cols-[11rem_1fr] sm:gap-4">
    <dt className="text-sm font-medium text-slate-500">{label}</dt>
    <dd className="mt-1 break-words text-sm text-slate-900 sm:mt-0">{value}</dd>
  </div>
);

const ExternalLink = ({ href, children }: { href: string; children: ReactNode }) => (
  <a className="font-medium text-blue-700 underline decoration-blue-300 underline-offset-4 hover:text-blue-900"
    href={href} target="_blank" rel="noreferrer">{children}</a>
);

const VersionCard = ({ label, version, detail }: { label: string; version: string; detail: string }) => (
  <Card className="p-5">
    <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">{label}</p>
    <p className="mt-2 font-mono text-2xl font-semibold text-slate-900">{version}</p>
    <p className="mt-2 text-sm text-slate-500">{detail}</p>
  </Card>
);

const OfficeTable = ({ offices, emptyMessage }: { offices: string[]; emptyMessage: string }) => (
  <div className="max-h-72 overflow-y-auto rounded-lg border border-slate-200">
    <Table>
      <TableHead className="sticky top-0 z-10 bg-white"><TableRow><TableHeader>Office</TableHeader></TableRow></TableHead>
      <TableBody>
        {offices.length ? [...offices].sort().map((office) => (
          <TableRow key={office}><TableCell>{office}</TableCell></TableRow>
        )) : <TableRow><TableCell>{emptyMessage}</TableCell></TableRow>}
      </TableBody>
    </Table>
  </div>
);

const VersionPane = () => {
  const application = useApplicationInfo();
  const schema = useSchemaInfo();
  if (application.isLoading) return <LoadingSpinner />;
  if (application.isError || !application.data) {
    return <Card role="alert" className="border-red-200 bg-red-50 p-5 text-red-800">
      Version information could not be loaded: {application.error?.message}
    </Card>;
  }
  const app = application.data;
  const accessTabs = [
    { name: "Available offices", content: <OfficeTable offices={app.user.offices} emptyMessage="No offices available" /> },
    { name: "Script administration", content: <OfficeTable offices={app.user.adminOffices} emptyMessage="No offices available" /> },
  ];

  return <section aria-labelledby="version-heading" className="space-y-5 py-6">
    <div><H2 id="version-heading">Version and environment</H2><Text>Signed in as {app.user.username}.</Text></div>
    <div aria-label="Application versions" className="grid gap-4 md:grid-cols-3">
      <VersionCard label="API version" version={app.apiVersion} detail={formatDate(app.buildTime)} />
      <VersionCard label="UI version" version={uiVersion} detail={formatDate(uiBuildTime)} />
      <VersionCard label="Schema version"
        version={schema.data?.version ?? (schema.isLoading ? "Loading…" : "Unavailable")}
        detail={schema.data?.description ?? schema.error?.message ?? "Reading applied migration"} />
    </div>
    <div className="grid gap-6 lg:grid-cols-2">
      <Card className="p-6"><H3>Deployment</H3><dl className="mt-3">
        <Detail label="Environment" value={app.environment} />
        <Detail label="API revision" value={app.buildRevision} />
        <Detail label="API base path" value={app.rootPath} />
        <Detail label="Authentication" value={app.authenticationEnvironment} />
        <Detail label="Job execution" value={app.jobRunner} />
      </dl></Card>
      <Card className="p-6"><H3>Database schema</H3>
        {schema.data ? <dl className="mt-3">
          <Detail label="Schema" value={schema.data.name} />
          <Detail label="Applied version" value={schema.data.version} />
          <Detail label="Latest migration" value={schema.data.description} />
          <Detail label="Installed" value={formatDate(schema.data.installedOn)} />
        </dl> : <Text className="mt-3">{schema.isLoading ? "Reading the applied schema version…" : schema.error?.message}</Text>}
      </Card>
      <Card className="p-6 lg:col-span-2"><H3>Your access</H3>
        <div className="mt-4"><Tabs tabs={accessTabs} fill /></div>
      </Card>
    </div>
  </section>;
};

const capabilities = [
  { title: "Discover approved jobs", description: "Browse the scripts available to your office and see the inputs each job needs." },
  { title: "Submit and monitor work", description: "Start batch jobs, follow their status, and review their output." },
  { title: "Manage office catalogs", description: "Authorized script administrators can maintain their office job definitions." },
];

const AboutOverview = () => <div className="space-y-8 py-6">
  <Card className="border-blue-200 bg-blue-50 p-6 sm:p-8">
    <H2>Use case</H2>
    <Text className="mt-3 max-w-4xl">
      Run approved batch jobs without direct access to the systems that execute them.
      Office assignments control which scripts and administrative actions are available.
    </Text>
    <Text className="mt-3 max-w-4xl">
      Batch Events replaces district cron jobs for approved operational work. Jobs are defined for
      an office, run when needed, and tracked with their status and output in the application.
    </Text>
  </Card>
  <section aria-labelledby="capabilities-heading"><H2 id="capabilities-heading">What you can do</H2>
    <div className="mt-4 grid gap-4 md:grid-cols-3">{capabilities.map((capability) => (
      <Card key={capability.title} className="p-5"><H3>{capability.title}</H3>
        <Text className="mt-2">{capability.description}</Text></Card>
    ))}</div>
  </section>
</div>;

const controls = [
  { action: "Review jobs you ran", access: "An authenticated account",
    result: "Jobs List shows jobs submitted by your username. It does not show every job for the office." },
  { action: "Execute a job", access: "An office role that matches one of the script's allowed roles",
    result: "Active, matching scripts appear under Submit Job. Most office scripts allow CWMS Users." },
  { action: "Define or change a job", access: "Data Acquisition Mgr or Data Exchange Mgr for the office",
    result: "Scripts Manager allows create, edit, and delete. The definition sets which roles may run it." },
];

const ControlsPane = ({ user }: { user?: ApplicationInfo["user"] }) => {
  const offices = user ? [...new Set([...Object.keys(user.roles), ...user.offices, ...user.adminOffices])].sort() : [];
  return <section aria-labelledby="controls-heading" className="space-y-6 py-6">
    <div><H2 id="controls-heading">Controls</H2>
      <Text>Batch Events uses office roles from your CDA profile. It does not assign or change roles.</Text>
    </div>
    <div className="overflow-x-auto rounded-lg border border-slate-200"><Table>
      <TableHead><TableRow><TableHeader>Action</TableHeader><TableHeader>Required access</TableHeader>
        <TableHeader>What happens</TableHeader></TableRow></TableHead>
      <TableBody>{controls.map((control) => <TableRow key={control.action}>
        <TableCell className="font-medium">{control.action}</TableCell><TableCell>{control.access}</TableCell>
        <TableCell>{control.result}</TableCell></TableRow>)}</TableBody>
    </Table></div>
    <Card className="p-6"><H3>How roles are set</H3>
      <div className="mt-3 space-y-3 text-sm text-slate-700">
        <p>Roles are managed in the CDA user profile and grouped by office.</p>
        <p><strong>CWMS Users</strong> makes an office available in Batch Events. A script can require
          that role or another role assigned to you for the same office.</p>
        <p><strong>Data Acquisition Mgr</strong> or <strong>Data Exchange Mgr</strong> allows you to
          define and maintain scripts for that office in Scripts Manager.</p>
        <p>The <strong>Roles</strong> field on each script definition controls who may execute it.</p>
        <p>See the <ExternalLink href={github.cda}>CWMS Data API repository</ExternalLink> for the
          source of CDA profile behavior and the{" "}
          <ExternalLink href={github.application}>Batch Events repository</ExternalLink> for this
          application's access checks.</p>
      </div>
    </Card>
    {user ? <Card className="p-6"><H3>Your current controls</H3>
      <Text className="mt-2">These values come from your current CDA profile.</Text>
      <div className="mt-4 max-h-80 overflow-auto rounded-lg border border-slate-200"><Table>
        <TableHead className="sticky top-0 z-10 bg-white"><TableRow><TableHeader>Office</TableHeader>
          <TableHeader>Assigned roles</TableHeader><TableHeader>Execute</TableHeader>
          <TableHeader>Define</TableHeader></TableRow></TableHead>
        <TableBody>{offices.map((office) => <TableRow key={office}>
          <TableCell className="font-medium">{office}</TableCell>
          <TableCell>{user.roles[office]?.join(", ") || "None reported"}</TableCell>
          <TableCell>{user.offices.includes(office) ? "Eligible scripts" : "No"}</TableCell>
          <TableCell>{user.adminOffices.includes(office) ? "Yes" : "No"}</TableCell>
        </TableRow>)}</TableBody>
      </Table></div>
    </Card> : <Card className="p-5"><Text>Sign in to compare these controls with your office roles.</Text></Card>}
  </section>;
};

type Callout = { label: string; style: CSSProperties };
const OnboardingScreenshot = ({
  src,
  alt,
  callouts,
  frameClassName,
}: {
  src: string;
  alt: string;
  callouts: Callout[];
  frameClassName: string;
}) => (
  <figure className="mx-auto mt-5 w-full min-w-0 max-w-4xl">
    <div className="w-full max-w-full rounded-lg">
      <div
        className={"relative min-w-0 overflow-hidden rounded-lg border border-slate-300 bg-white shadow-sm " + frameClassName}
      >
        <img src={src} alt={alt} className="absolute inset-x-0 top-0 block h-auto w-full max-w-none" />
        {callouts.map((callout) => <div key={callout.label} aria-hidden="true"
          className="absolute hidden rounded-full border-4 border-red-600 shadow-[0_0_0_2px_white] sm:block"
          style={callout.style}>
          <span className="absolute -top-8 left-0 whitespace-nowrap rounded bg-red-700 px-2 py-1 text-xs font-semibold text-white shadow">
            {callout.label}
          </span>
        </div>)}
      </div>
    </div>
    <figcaption className="mt-2 text-sm text-slate-600">
      {alt}{" "}
      <a
        href={src}
        target="_blank"
        rel="noreferrer"
        className="font-medium text-blue-700 underline decoration-blue-300 underline-offset-4"
      >
        Open full-size screenshot
      </a>
    </figcaption>
  </figure>
);

const OnboardingStep = ({ number, title, children }: { number: number; title: string; children: ReactNode }) => (
  <li><Card className="p-5 sm:p-6"><div className="flex gap-4">
    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-blue-700 font-semibold text-white">{number}</span>
    <div className="min-w-0 flex-1"><H3>{title}</H3>
      <div className="mt-2 space-y-3 text-sm text-slate-700">{children}</div></div>
  </div></Card></li>
);

const OnboardingSubstep = ({
  number,
  title,
  children,
}: {
  number: string;
  title: string;
  children: ReactNode;
}) => (
  <li className="min-w-0 rounded-lg border border-slate-200 bg-slate-50 p-4 sm:p-5">
    <div className="flex flex-col gap-3 sm:flex-row">
      <span className="flex h-8 min-w-12 shrink-0 items-center justify-center rounded-full bg-slate-700 px-2 text-sm font-semibold text-white">
        {number}
      </span>
      <div className="min-w-0 flex-1">
        <h4 className="font-semibold text-slate-900">{title}</h4>
        <div className="mt-2 space-y-3">{children}</div>
      </div>
    </div>
  </li>
);

const OnboardingPane = ({ user }: { user?: ApplicationInfo["user"] }) => {
  const office = user?.adminOffices.includes("SWT")
    ? "SWT"
    : user?.adminOffices[0] ?? user?.offices[0];
  const canDefine = office ? user?.adminOffices.includes(office) : false;
  const officeLabel = office ?? "OFFICE";
  const officeRepoSearch = "https://github.com/orgs/USACE-WaterManagement/repositories?q=" +
    officeLabel.toLowerCase() + "-wm-cwbi-jobs";
  return <section aria-labelledby="onboarding-heading" className="space-y-6 py-6">
    <div><H2 id="onboarding-heading">Set up and run a job</H2>
      <Text>Follow these steps to add an office job, run it, and review the result.</Text></div>
    <Card className="border-blue-200 bg-blue-50 p-5">
      {office ? <Text>This walkthrough uses <strong>{office}</strong> from your current office access.{" "}
        {canDefine ? "You can define and execute eligible jobs for this office."
          : "You can execute eligible jobs, but an office script administrator must define them."}
      </Text> : <Text>Sign in to replace OFFICE with one of your offices.</Text>}
    </Card>
    <ol className="space-y-6">
      <OnboardingStep number={1} title="Confirm your office access">
        <p>Open the <strong>Controls</strong> tab above. To define a job for {officeLabel}, your CDA
          profile needs <strong>Data Acquisition Mgr</strong> or <strong>Data Exchange Mgr</strong> for
          that office. To run it, you need an office role allowed by the script.</p>
        <p>If a role is missing, contact the person who manages CDA user roles for your office.</p>
      </OnboardingStep>
      <OnboardingStep number={2} title="Prepare the job in your office repository">
        <p>Commit the executable script to the {officeLabel} office job repository. The convention is
          an office repository such as <code>lrh-wm-cwbi-jobs</code> or <code>swt-wm-cwbi-jobs</code>.</p>
        <p>Find a repository with this <ExternalLink href={officeRepoSearch}>{officeLabel} repository search</ExternalLink>,
          or review the <ExternalLink href={github.lrhJobs}>LRH</ExternalLink> and{" "}
          <ExternalLink href={github.swtJobs}>SWT</ExternalLink> examples. Setup conventions are in the{" "}
          <ExternalLink href={github.application + "#readme"}>Batch Events README</ExternalLink>.</p>
      </OnboardingStep>
      <OnboardingStep number={3} title="Define the job">
        <p>Use Scripts Manager to add the office script in two parts.</p>
        <ol className="mt-4 space-y-5">
          <OnboardingSubstep number="3.1" title="Choose the office and start a definition">
            <p>Open <strong>Scripts Manager</strong>, choose {officeLabel}, then select <strong>New +</strong>.</p>
            <OnboardingScreenshot
              src="/events/about/onboarding-scripts-manager.png"
              alt="Scripts Manager with the office selector and New button marked."
              frameClassName="aspect-[16/5]"
              callouts={[
                { label: "Choose " + officeLabel, style: { left: "1%", top: "39%", width: "12%", height: "12%" } },
                { label: "Select New +", style: { left: "43%", top: "51%", width: "9%", height: "14%" } },
              ]}
            />
          </OnboardingSubstep>
          <OnboardingSubstep number="3.2" title="Complete the job definition">
            <p>Enter a name and description. <strong>GitHub Repo Path</strong> is the path to the
              script inside the office repository, such as <code>python/my_job.py</code>—not a GitHub URL.</p>
            <p>Select the roles allowed to run the job, keep it active, and save.</p>
            <OnboardingScreenshot
              src="/events/about/onboarding-script-form.png"
              alt="New script form with the repository path and roles fields marked."
              frameClassName="aspect-[16/9]"
              callouts={[
                { label: "Repository path", style: { left: "63%", top: "56%", width: "35%", height: "9%" } },
                { label: "Allowed roles", style: { left: "63%", top: "68%", width: "35%", height: "15%" } },
              ]}
            />
          </OnboardingSubstep>
        </ol>
      </OnboardingStep>
      <OnboardingStep number={4} title="Execute the job">
        <ol className="mt-4 space-y-5">
          <OnboardingSubstep number="4.1" title="Choose the office and script">
            <p>Open <strong>Submit Job</strong>, select {officeLabel}, then choose the script.
              Only active scripts that allow one of your {officeLabel} roles are listed.</p>
            <OnboardingScreenshot
              src="/events/about/onboarding-submit-job.png"
              alt="Submit Job with the office, script, and Execute controls marked."
              frameClassName="aspect-[16/5]"
              callouts={[
                { label: "Choose " + officeLabel, style: { left: "1%", top: "39%", width: "12%", height: "12%" } },
                { label: "Choose script", style: { left: "1%", top: "59%", width: "31%", height: "13%" } },
                { label: "Execute", style: { left: "1%", top: "76%", width: "8%", height: "14%" } },
              ]}
            />
          </OnboardingSubstep>
          <OnboardingSubstep number="4.2" title="Review inputs and execute">
            <p>Enter any parameters required by the selected script, review the values, then select
              <strong> Execute</strong>.</p>
          </OnboardingSubstep>
        </ol>
      </OnboardingStep>
      <OnboardingStep number={5} title="Review the result">
        <p>Open <strong>Jobs List</strong>. Select <strong>Details</strong> for the run to review its
          status and output. This list contains jobs submitted by your username, not every job for
          {office ? " " + office : " the office"}.</p>
      </OnboardingStep>
    </ol>
  </section>;
};

export type AboutTab = "about" | "controls" | "onboarding" | "version";

export const AboutPage = ({ initialTab = "about" }: { initialTab?: AboutTab }) => {
  const auth = useAuth();
  const application = useApplicationInfo();
  const user = auth.isAuth ? application.data?.user : undefined;
  const tabs = [
    { name: "About", content: <AboutOverview /> },
    { name: "Controls", content: <ControlsPane user={user} /> },
    { name: "Onboarding", content: <OnboardingPane user={user} /> },
    ...(auth.isAuth ? [{ name: "Version", content: <VersionPane /> }] : []),
  ];
  const requestedTabIndex = {
    about: 0,
    controls: 1,
    onboarding: 2,
    version: 3,
  }[initialTab];
  const defaultTabIndex =
    requestedTabIndex === 3 && !auth.isAuth ? 0 : requestedTabIndex;

  return <div className="mx-auto max-w-6xl">
    <section className="space-y-4 py-4">
      <H1>About CWMS Batch Events</H1>
      <Text className="max-w-3xl text-lg">CWMS Batch Events is the web interface for finding,
        starting, and monitoring approved water management batch jobs. It keeps job execution,
        status, and office-specific access together in one application.</Text>
    </section>
    <Tabs
      key={initialTab + String(auth.isAuth)}
      tabs={tabs}
      defaultIndex={defaultTabIndex}
    />
  </div>;
};
