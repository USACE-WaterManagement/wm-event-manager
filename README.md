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

#### Script Containers
The API will reference district script docker images that exist locally by the name `[office-code]-jobs`, e.g. `lrh-jobs`.  These can be created by cloning the corresponding district jobs repo, e.g. [lrh-wm-cwbi-jobs](https://github.com/USACE-WaterManagement/lrh-wm-cwbi-jobs), and building the images from the local dockerfile with `docker build . -t [office-code]-jobs`.

#### Script Catalogs
Available district scripts are managed within the cwms-batch application itself using the "Scripts Manager" available through the Web UI or directly through API endpoints.

#### User Interface
The user interface is deployed locally as a vite development server.  To run it, simply enter the `ui` directory and run `npm run dev`.

#### Failed-job email notifications

Batch Events stores office-scoped email templates and one active failed-job rule
per script. Reusable recipient lists are owned by CDA, not Batch Events. A rule
stores the CDA list ID together with the script office, so the effective list
identity is `(office, user-list-id)`. Users create and maintain list membership
in the authenticated CDA User Lists UI; Batch Events only selects and resolves
those lists.

CDA resolution at job-failure time uses a registered confidential Keycloak
service account with `CDA_CLIENT_ID` and `CDA_CLIENT_SECRET`. `CDA_TOKEN_URL` can
override the normal token URL derived from `AUTH_HOST` and `AUTH_REALM`, and
`CDA_TOKEN_HOST_HEADER` is available for local proxy routing. API keys are not
used for this workflow.

The notification worker uses `NOTIFICATION_DELIVERY_MODE=log` locally, which
records only delivery metadata and does not log recipients or message contents.
Set the mode to `ses` and provide `NOTIFICATION_FROM_ADDRESS` for AWS SES
delivery. Failed or invalid deliveries remain on SQS for retry and eventual
dead-letter handling. Templates are rendered in a restricted Jinja sandbox and
may reference only the documented job-failure fields exposed by Batch Events.
