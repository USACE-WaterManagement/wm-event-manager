# wm-event-manager

The Water Management Event Manager provides users an API and user interface to execute water management jobs on a manual or event-driven basis.

## Local Development Setup

### Python
For the best experience, [pyenv](https://github.com/pyenv/pyenv) is recommended.  If pyenv is available, the `setup-pyenv.sh` script is provided to create a virtual environment and install the necessary local dev requirements.

### Authentication
By default, the local instance of the API uses a mock user account.  This account has script-execute permissions for all districts.  As a result, the API will return scripts for all offices that contain a corresponding script catalog within the minio instance.

### Script Containers
The API will reference district script docker images that exist locally by the name `[code]-jobs`, e.g. `lrh-jobs`.  These can be created by cloning the corresponding district jobs repo, e.g. [lrh-wm-cwbi-jobs](https://github.com/USACE-WaterManagement/lrh-wm-cwbi-jobs), and building the images from the local dockerfile with `docker build . -t [code]-jobs`.

### Script Catalogs
After running the api's docker compose file, minio can be accessed at `http://localhost:9001`.  In the minio instance, create a bucket named `wm-web-internal-dev`.  Add the office code and repo path for any locally-available district job containers to `api/scripts/catalog_config.toml`. Then, run `api/scripts/build_catalogs.py`. This will generate a `scripts_catalog.json` object under each available district's prefix within minio.

### User Interface
The user interface is deployed locally as a vite development server.  To run it, simply enter the `ui` directory and run `npm run dev`.