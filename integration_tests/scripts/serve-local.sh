#!/bin/sh

VERSION=latest
docker run --rm\
    -e CI=1\
    -e DISABLE_TELEMETRY=true\
    -e GORILLA_FRONTEND_HOST=http://localhost:9000\
    -d\
    --name wandb_local \
    wandb/local:$VERSION
