#!/bin/bash
cd fsd_medic
git pull
docker compose -f docker-compose.prod.yaml up --build -d
