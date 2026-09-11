import { createFileRoute, Link } from "@tanstack/react-router";
import { H1, H2 } from "@usace/groundwork";

export const Route = createFileRoute("/help_/script-files")({
  component: ScriptFilesGuide,
});

function ScriptFilesGuide() {
  return <article className="mx-auto max-w-[52rem] leading-[1.65] [&_a]:text-blue-700 [&_a]:underline [&_p]:my-4 [&_h2]:mt-8 [&_pre]:overflow-x-auto [&_pre]:rounded-md [&_pre]:border [&_pre]:border-gray-300 [&_pre]:bg-gray-50 [&_pre]:p-4 [&_pre]:text-sm">
    <H1>Adding script files</H1>
    <p>Scripts Manager registers jobs and selects existing files. You cannot create directories, create files, or edit file contents in this UI. Clone your district’s GitHub repository to make those changes locally, then submit them through your district’s review process.</p>
    <H2>1. Get access and clone your district repository</H2>
    <p>Sign in to GitHub with an account that has access to your district’s scripts repository. Ask the repository maintainer for access if needed. Use the repository configured for your office, shown beneath GitHub Repo Path in Scripts Manager. The GitHub button in the application header opens the jobs repository for the selected office. Confirm the repository shown in the dialog before continuing.</p>
    <p>For SWT, clone the scripts repository and create a branch from the branch your district uses for jobs:</p>
    <pre><code>{`git clone https://github.com/USACE-WaterManagement/swt-wm-cwbi-jobs.git
cd swt-wm-cwbi-jobs
git switch <configured-branch>
git pull --ff-only
git switch -c add-daily-report`}</code></pre>
    <p>Replace <code>{"<configured-branch>"}</code> with the branch configured for your office. The file browser shows the repository and branch above the folder list.</p>
    <H2>2. Create and test the file locally</H2>
    <p>Create any needed directories in your clone using your editor or file manager. For example, add <code>python/reports/daily_report.py</code>. Test the script with the runtime and arguments it will use. Keep credentials out of scripts and commits.</p>
    <pre><code>{`python python/reports/daily_report.py`}</code></pre>
    <p>For Bash, test with <code>bash path/to/script.sh</code>. For a built Java JAR, test with <code>java -jar path/to/program.jar</code> and follow your district’s process for making the JAR available to the job.</p>
    <H2>3. Commit, push, and request review</H2>
    <pre><code>{`git add python/reports/daily_report.py
git commit -m "Add daily report script"
git push -u origin add-daily-report`}</code></pre>
    <p>Open a pull request in the district repository targeting the configured branch. After review and merge, confirm the file exists on that branch before registering the job.</p>
    <H2>4. Register the job</H2>
    <p>Open <Link to="/scripts-manager">Scripts Manager</Link>, select <strong>SWT</strong>, and choose <strong>New +</strong>. Select <strong>District GitHub repository</strong> as the source and the matching runtime. Browse to the file or type its repository-relative path, such as <code>python/reports/daily_report.py</code>. Add the required arguments and roles, then save.</p>
    <p>The browser filters files for the selected runtime. Use <strong>All files</strong> when needed. Saving a script definition does not create or upload a file in GitHub.</p>
    <p>Jobs that use an <strong>Installed command</strong> do not need a repository file. Select that source when the command is already available in the job image.</p>
  </article>;
}
