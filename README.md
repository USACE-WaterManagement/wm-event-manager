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
By default, the local instance of the API uses a mock user account.  This account has script-execute permissions for all districts.  As a result, the API will return scripts for all offices that contain a corresponding script catalog within the minio instance.

#### Job Registry
Available office jobs are managed in Batch Events using the "Scripts Manager" in the Web UI or the `/scripts` API endpoints. A registry entry defines the office, repository path, runtime (`python`, `node`, `java`, or `shell`), command arguments, resource profile (`small`, `medium`, or `large`), timeout, optional environment variables, allowed secret names, roles, and optional schedule.

Scheduled jobs are also registry-driven. Airflow calls `/scripts/scheduled`, filters jobs due for the current minute, and triggers them through `/jobs`. This keeps office timing and resource choices in Batch Events instead of duplicating one Airflow or AWS Batch definition per office.

#### Runtime Containers
Production uses shared AWS Batch job definitions per runtime rather than per-office job definitions. The shared runner image is built from `cwbi-wm-images`, clones the office repository at runtime, asks Batch Events for the job's brokered runtime environment, and then runs the registered script path with the registry's command arguments and timeout.

AWS Batch container logs are written to shared runtime log groups. Batch Events keeps the office on each job record and exposes office-scoped job listing for office admins, so district users can filter to their office in the Jobs List and open logs for individual jobs without requiring one CloudWatch log group or job definition per office.

Local development can still run office containers directly when needed, but the production-shaped path is the shared runner plus Batch Events runtime broker. Office-specific CDA Keycloak client credentials should be stored in the office-group job secret and exposed only through the registry entry's allowed secret names, such as `CDA_CLIENT_ID` and `CDA_CLIENT_SECRET`.

#### User Interface
The user interface is deployed locally as a vite development server.  To run it, simply enter the `ui` directory and run `npm run dev`.
