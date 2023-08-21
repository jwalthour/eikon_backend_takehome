#!/bin/bash

# Start both the ETL+API service and the database service to support it.
docker compose up
# Note: If you just want to run the ETL+API service, you can 
# 1. Edit compose.yaml to remove the database server, or
# 2. run the following command instead:
# docker run --name etl-server -p 127.0.0.1:5000:5000 -e ROOT_DATA_PATH=./data/ -e DB_HOSTNAME=user-experiment-stats -e DB_PORT_NUM=5432 -e DB_USERNAME=postgres -e DB_PASSWORD=22jXXTL2aSdKu8xFjpS9V_4lADSQlr55 -d eikon_backend
