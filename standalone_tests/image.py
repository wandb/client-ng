import time
import numpy as np
import wandb


IMG_WIDTH = 5
IMG_HEIGHT = 5

IMG_COUNT = 2
# Step count
N = 5


def gen_image(w=IMG_WIDTH, h=IMG_HEIGHT):
    return np.concatenate(
        (np.random.rand(h//2, w),
         np.zeros((h//2, w))),
        axis=0)

all_tests = {
    "test_image_file_single": wandb.Image("../tests/fixtures/wb.jpeg"),
    "test_image_file_array": [wandb.Image("../tests/fixtures/wb.jpeg")],
    "test_image_data_single": wandb.Image(gen_image()),
    "test_image_data_array": [wandb.Image(gen_image()) for _ in range(IMG_COUNT)],
}

if __name__ == "__main__":
    wandb.init(project='image-test')

    for i in range(0, N):
        log = all_tests
        log.update({"i": i})
        wandb.log(log, step=i)
