#!/bin/bash
set -e

PAYS=("bresil" "equateur" "colombie")

for pays in "${PAYS[@]}"; do
    echo "Build image futurekawa-$pays"
    docker build -t futurekawa-$pays pays/$pays/api
    docker push futurekawa-$pays
done

echo "Build image futurekawa-siege-api"
docker build -t futurekawa-siege-api siege/api
docker push futurekawa-siege-api

echo "Build image futurekawa-siege-front"
docker build -t futurekawa-siege-front siege/frontend
docker push futurekawa-siege-front
