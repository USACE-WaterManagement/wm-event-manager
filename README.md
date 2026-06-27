# cwms-batch-events

CWMS Batch Events provides users an API and user interface to execute water management jobs on a manual or event-driven basis.

## Contributions

To get your local environment setup and/or make contributions please see the contributions documentation: [CONTRIBUTING.md](https://github.com/USACE-WaterManagement/cwms-batch-events/blob/cwbi-dev/CONTRIBUTING.md)


### Local Development Setup

#### Critical URLs
page | url
---- | ---
ElasticMQ Web Interface | http://localhost:9325
Minio Web Interface | http://localhost:9001
Web Dev Server | http://localhost:5173
Swagger Docs | http://localhost:8000/docs
Redoc | http://localhost:8000/redoc

#### Python
For the best experience, [pyenv](https://github.com/pyenv/pyenv) is recommended for install instructions.  If pyenv is available, the `setup-pyenv.sh` script is provided to create a virtual environment and install the necessary local dev requirements. Be sure to install `gcc` for your environment.

#### Authentication
By default, the local instance of the API can use a mock user account. This account has script-execute permissions for all districts. Available scripts come from the Batch Events database registry, so local development should seed or manage script rows through migrations, the "Scripts Manager" UI, or the `/scripts` API endpoints.

#### Job Registry
Available office jobs are managed in Batch Events using the "Scripts Manager" in the Web UI or the `/scripts` API endpoints. A registry entry defines the office, repository path, runtime (`python`, `node`, `java`, or `shell`), command arguments, resource profile (`small`, `medium`, or `large`), timeout, optional environment variables, allowed secret names, roles, and optional schedule. A script can run a direct file such as `python/my_job.py` or a shell entrypoint such as `bin/hourly.sh`; the registry owns the command and arguments, so the old `hourly.sh` convention is no longer required for every job.

Scheduled jobs are also registry-driven. Airflow calls `/scripts/scheduled`, filters jobs due for the current logical date, and triggers them through `/jobs`. The registry supports hourly-at-minute entries and five-field cron expressions, which keeps office timing and resource choices in Batch Events instead of duplicating one Airflow or AWS Batch definition per office.

#### Runtime Containers
Production uses shared AWS Batch job definitions per runtime rather than per-office job definitions. The shared runner image is built from `cwbi-wm-images`, clones the office repository at runtime, asks Batch Events for the job's brokered runtime environment, and then runs the registered script path with the registry's command arguments and timeout.

The dispatcher chooses the runtime command from the script registry runtime:
`python`, `node`, `java`, or `bash` for `shell`. Shell entrypoints such as
`bin/hourly.sh` should be registered with the `shell` runtime rather than
depending on a language-specific job definition to invoke bash.

AWS Batch container logs are written to shared runtime log groups. Batch Events keeps the office on each job record and exposes office-scoped job listing and log lookup for office admins, so district users can filter to their office in the Jobs List and open logs for individual jobs without requiring one CloudWatch log group or job definition per office.

Local development can still run office containers directly when needed, but the production-shaped path is the shared runner plus Batch Events runtime broker. Office-specific CDA Keycloak client credentials should be stored in the office-group job secret and exposed only through the registry entry's allowed secret names, such as `CDA_CLIENT_ID` and `CDA_CLIENT_SECRET`.

Deployments can override the default AWS Batch runtime wiring with JSON environment values:

| Variable | Purpose |
| --- | --- |
| `BATCH_RUNTIME_JOB_DEFINITIONS` | Maps registry runtimes to AWS Batch job definition names. Defaults to `cwms-python-runner-jobdef`, `cwms-node-runner-jobdef`, `cwms-java-runner-jobdef`, and `cwms-shell-runner-jobdef`. |
| `BATCH_RESOURCE_PROFILES` | Maps registry resource profiles to AWS Batch `VCPU` and `MEMORY` overrides. Defaults to `small`, `medium`, and `large`. |
| `BATCH_RUNTIME_COMMANDS` | Maps registry runtimes to the command prefix used in the shared runner container. Defaults to `python`, `node`, `java`, and `bash` for shell entrypoints. |
| `BATCH_LOG_GROUP_PREFIX` | Prefix for shared runtime CloudWatch log groups. Defaults to `ecs/cwms-batch`, producing groups such as `ecs/cwms-batch/shell-runner`. |

For example: `BATCH_RUNTIME_JOB_DEFINITIONS={"python":"cwms-python-runner-jobdef"}`.

#### User Interface
The user interface is deployed locally as a vite development server.  To run it, simply enter the `ui` directory and run `npm run dev`.
