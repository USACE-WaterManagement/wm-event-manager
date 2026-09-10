# Registered commands

Script administrators can select a district repository file or an installed command in Scripts Manager. Jobs continue to use the existing office AWS Batch job definition, credentials, queue, and logs. This feature does not need Airflow or a new Keycloak account.

| Source | Runtime / executable | Path / arguments | Container command |
| --- | --- | --- | --- |
| District GitHub repository | Python | `python/report.py` | `python /jobs/python/report.py` |
| District GitHub repository | Java JAR | `lib/report.jar` | `java -jar /jobs/lib/report.jar` |
| District GitHub repository | Bash | `bin/report.sh` | `bash /jobs/bin/report.sh` |
| Installed command | `java` | `-jar`, `/opt/report.jar`, `two words` | `java -jar /opt/report.jar 'two words'` |

Enter one argument per line in the form. The API stores `commandArgs` as an array, preserving spaces and literal shell characters. Commands execute directly; shell expressions require an explicit `bash` executable with `-lc` and the expression as separate arguments. The runtime selector applies to repository files; an installed command supplies its executable directly.

Installed commands skip district repository checkout and repository Python dependency installation. Their executable and artifacts must already be available in the image/container; downloading or building a JAR is outside this feature. Existing Python registrations and queued messages keep their default behavior.

Deploy the supporting `cwbi-wm-images` command-runner change before enabling installed commands. Apply the database migration and deploy both API and dispatcher before using the new fields. The image alone does not make an old dispatcher understand registered commands. No `cwms-batch` infrastructure or shared-runtime job definitions are required.

Runtime and arguments are copied into the job record and queue message when submitted, so later script edits do not change an already submitted job. Local Docker execution uses the same command construction as AWS Batch.
