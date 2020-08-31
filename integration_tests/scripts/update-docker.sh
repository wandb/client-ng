cp ../requirements.txt ./requirements_main.txt
docker build -t nicholasbardy/wandb-integration:$VERSION .
rm ./requirements_main.txt
docker push nicholasbardy/wandb-integration:$VERSION
