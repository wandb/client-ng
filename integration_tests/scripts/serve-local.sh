#!/bin/sh

VERSION=latest
docker run --rm\
    -e CI=1\
    -e DISABLE_TELEMETRY=true\
    -d\
    -p 8080:8080 -p 3306:3306  \
    --name wandb_local \
    wandb/local:$VERSION
