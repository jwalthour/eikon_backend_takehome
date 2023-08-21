#!/bin/bash

# Call the API and command the ETL job to begin processing.
curl http://localhost:5000/start_etl -X POST -F userExperiments=user_experiments.csv -F users=users.csv -F compounds=compounds.csv
