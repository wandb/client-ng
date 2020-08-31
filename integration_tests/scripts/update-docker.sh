cp ../requirements.txt ./requirements_main.txt
docker build -t wandb/local-integration:$VERSION .
rm ./requirements_main.txt
docker push wandb/local-integration:$VERSION
