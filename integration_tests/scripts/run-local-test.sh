#!/bin/sh
jupyter notebook &
scripts/serve-local.sh

rm -rf wandb/* &&\
  DEBUG=wandb:*\
  CYPRESS_DEV=TRUE\
  CYPRESS_WANDB_BASE_URL=http://localhost:9000\
  CYPRESS_ENVIRONMENT=local\
  CYPRESS_MYSQL_URI=mysql://wandb_local:wandb_local@127.0.0.1:3306/wandb_local\
  npx cypress open --browser chrome
