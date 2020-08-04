import wandb
from test_scripts.media.all_media_types import run_tests, all_tests

def test_all_media():
    api = wandb.Api()
    run_path = run_tests()
    # run_path = "all-media-test/runs/lbabj5x4"
    run = api.run("local/" + run_path)

    history = run.history()

    for index, row in history.iterrows():
        # print(row)
        for k, v in all_tests.items():
            history_object = row[k]
            print("asset row" + k)
            assert history_object != None
