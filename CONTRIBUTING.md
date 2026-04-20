# Contributions

## Pre-reqs
* VM 
* Python 3.12+ (Pref with `pyenv`)
* Docker 
* NodeJS 

## Getting Started

1. Setup the `pyenv` env (Details below)
    1. Run `./setup-pyenv.sh`
2. For each office that you want to install:
    1. Clone the repo with: `git clone https://github.com/usace-watermanagement/swt-wm-cwbi-jobs`
    2. Change directory into the cloned repo
    3. Build the local container for jobs after cloning with: `docker build . -t swt-jobs`
3. Start the API Server **(From the project root)**
    1. Create the `cwms` docker network with: `docker network create cwms`
    2. Start the API server environment with `docker compose up`   
4. Start the Web Interface **(From the project root)**
    1. `cd ui`
    2. Install Packages (NodeJS required): `npm install`
    3. Run the local development vite server: `npm run dev`

## Notes
* Type Standardization
  * TypeScript types are generated from the API for use in the frontend using [OpenAPI TypeScript](https://openapi-ts.dev/). 
  * If API types are updated or modified, run `npm run generate:types` to update the type definitions.
* Python Testing
  * Run `pytest` from the project root to execute the Python unit test suite.
  * The suite is configured to report coverage for `cwms_batch_events` and should stay fast and free of external dependencies.
