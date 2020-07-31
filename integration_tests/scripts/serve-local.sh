#!/bin/sh

VERSION=0.9.12
docker run --rm\
    -e CI=1\
    -e DISABLE_TELEMETRY=true\
    -e GORILLA_FRONTEND_HOST=http://localhost:9000\
    -d\
    -v wandb:/vol\
    -p 9000:8080 -p 3306:3306 -p 8083:8083 -p 9001:9000\
    --name wandb_local \
    wandb/local:$VERSION
