# District job schedules

Scripts Manager supports manual execution, an hourly minute (0–59), or a numeric five-field cron expression, with an IANA timezone such as `America/Chicago`. Existing registrations default to disabled schedules and UTC. Script administrators enable schedules; the scheduler catalog includes only active, enabled scripts authorized for its account's office roles.

`GET /scripts/scheduled` returns the authorized schedule catalog. The supporting `airflow-config` DAG evaluates each row in its selected timezone and calls the existing `POST /jobs` endpoint. Spring daylight-saving gaps are skipped and repeated fall times run once. Manual jobs continue working independently.

Saving a schedule does not itself start a scheduler. Deploy the supporting Airflow DAG, configure its credentials, and unpause it before expecting automatic runs. Remove the corresponding office/job from the existing hourly/daily DAG configuration when moving it, to avoid duplicate execution.

The initial scheduler uses existing CDA API-key authentication. Provision a dedicated authorized CDA account/key, grant the roles required by the registered jobs, and configure `BATCH_EVENTS_API_ROOT` plus `BATCH_EVENTS_API_KEY` in Airflow's secret-backed variables. Optional office-specific `BATCH_EVENTS_API_KEY_<OFFICE>` values and `BATCH_EVENTS_SCHEDULED_OFFICES` restrict rollout by office. Scheduler credentials remain in Airflow; they are not passed into district jobs. No new Keycloak client is required by this extraction. A later switch to Keycloak client credentials requires the separate M2M authentication work and provisioned clients.

The API/UI schedule PR can be reviewed independently of the runtime PR. Actual scheduled execution depends on the supporting Airflow configuration PR. It works with today's Python dispatcher; Java/Bash/installed commands additionally require the separate runtime feature.
