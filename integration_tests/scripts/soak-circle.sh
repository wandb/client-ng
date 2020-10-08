BRANCH=$(git branch --show-current);

for run in {1..N}
do
curl -u ${CIRCLE_API_USER_TOKEN}: \
     -d build_parameters[CIRCLE_JOB]=integration \
     https://circleci.com/api/v1.1/project/github/wandb/client-ng/tree/$BRANCH
sleep 1
done
