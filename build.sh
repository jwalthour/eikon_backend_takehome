#!/bin/bash

docker pull postgres
docker build -t eikon_backend .
