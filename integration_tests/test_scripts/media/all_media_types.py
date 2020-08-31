import numpy as np
import wandb

from util import all_tests, project_name

IMG_WIDTH = 5
IMG_HEIGHT = 5

IMG_COUNT = 2
# Step coun
N = 3

def run_tests():
    wandb.init(project=project_name)
    for _ in range(0, N):
        wandb.log(all_tests)

    run_path = project_name + "/" + wandb.run.id
    wandb.join()
    return run_path

if __name__ == "__main__":
    run_tests()
