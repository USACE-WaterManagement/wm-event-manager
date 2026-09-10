# Registered commands

Script administrators can select a district repository file or an installed command in Scripts Manager. Jobs use the office AWS Batch job definition, credentials, queue, and logs.

| Source | Runtime / executable | Path / arguments | Container command |
| --- | --- | --- | --- |
| District GitHub repository | Python | `python/report.py` | `python /jobs/python/report.py` |
| District GitHub repository | Java JAR | `lib/report.jar` | `java -jar /jobs/lib/report.jar` |
| District GitHub repository | Bash | `bin/report.sh` | `bash /jobs/bin/report.sh` |
| Installed command | `cwms-cli` | `blob`, `upload`, `--help` | `cwms-cli blob upload --help` |

Enter one argument per line in the form. The API stores `commandArgs` as an array, preserving spaces and literal shell characters. Commands execute directly; shell expressions require an explicit `bash` executable with `-lc` and the expression as separate arguments. The runtime selector applies to repository files; an installed command supplies its executable directly.

Installed commands skip district repository checkout and repository Python dependency installation. Their executable and files, including any JAR, must be available in the container before execution.

For example, `cwms-cli` is already installed in the runner image. A job can create a file and upload it as a CWMS blob without a district script in GitHub, avoiding the checkout and dependency installation time.

In Scripts Manager, register the script with these values:

| Field | Value |
| --- | --- |
| Office | `SWT` |
| Name | Upload job status |
| Source | Installed command |
| Executable | `bash` |

Enter these two lines in **Arguments**:

```text
-lc
printf 'Job completed\n' > /tmp/job-status.txt && cwms-cli blob upload --input-file /tmp/job-status.txt --blob-id JOB-STATUS --media-type text/plain --office SWT
```

The second line is one argument. Bash runs the upload only if file creation succeeds. The job environment supplies `CDA_API_ROOT` and `CDA_API_KEY` for the target CDA service. Use a unique blob ID for each output, or add `--overwrite` to replace an existing blob. Save the registration, then run it from **Submit Job**.

Runtime and arguments are copied into the job record and queue message when submitted, so later script edits do not change an already submitted job. Local Docker execution uses the same command construction as AWS Batch.
