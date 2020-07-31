import wandb
from integration_tests.test_scripts.media.all_media_types import run_tests, all_tests

api = wandb.Api()
# run_path = run_tests()
# run = api.run("local/" + run_path)

run_path = "all-media-test/runs/lbabj5x4"
run = api.run("local/" + run_path)

history = run.history()
# import ipdb; ipdb.set_trace()


for index, row in history.iterrows():
    print(row)
    for k,v in all_tests.items():
        path = row[k]['path']

        if path != None:
            print("downloading ", path)
            run.file(path).download()


# import ipdb; ipdb.set_trace()

# run = api.run("local/all-media-test/runs/rutypxhq")
# print(run)
