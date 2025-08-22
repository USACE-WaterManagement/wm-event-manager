# Contributions

## Pre-reqs
* VM 
* Python 3.12+ (Pref with `pyenv`)
* Docker 
* NodeJS 

## Getting Started

1. Setup the `pyenv` env (Details below)
    1. Run `./setup-pyenv.sh`
2. For each office that you want to install run:
    1. Clone the repo with: `git clone https://github.com/usace-watermanagement/swt-wm-cwbi-jobs`
    2. Change directory into the cloned repo
    3. Build the local container for jobs after cloning with: `docker build . -t swt-jobs`
3. Start the API Server **(From the project root)**
    1. Run `cd api`
    2. Create the `cwms` docker network with: `docker network create cwms`
    2. Start the API server environment with `docker compose up`   
4. Create the bucket in MiniIO for Objects
    1. Open MinIO in the browser
    2. Enter the login credentials from `api\docker-compose.yml` - They are: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
    3. Click the `+` and create a bucket with the name `wm-web-internal-dev` (Hard coded currently)
5. Populate the script catalogs from step #2
    1. Enter the local repositories you have cloned from step #2 into this file:   
    `/home/rocky/projects/wm-event-manager/api/scripts/catalog_config.toml`  
    *NOTE:* Absolute paths are recommended!
    2. Jump to the catalog directory: `cd api/scripts`
    3. Run the catalog script: `python3 build_catalogs.py`
6. Start the Web Interface **(From the project root)**
    1. `cd ui`
    2. Install Packages (NodeJS required): `npm install`
    3. Run the local development vite server: `npm run dev`

