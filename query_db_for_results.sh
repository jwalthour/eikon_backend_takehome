#!/bin/bash

# Connect to the database and display any results from the ETL job.
echo '\pset pager off \\ select * from user_experiment_stats;' | PGPASSWORD=2jXXTL2aSdKu8xFjpS9V_4lADSQlr55 psql -h localhost -U postgres -p 5432