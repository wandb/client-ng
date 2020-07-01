import numpy as np
import wandb

wandb.init(project='image-test')


IMG_WIDTH = 5
IMG_HEIGHT = 5
IMG_COUNT = 5
# Step count
N = 10


def gen_image(w=IMG_WIDTH, h=IMG_HEIGHT):
    return np.concatenate(
        (np.random.rand(h//2, w),
         np.zeros((h//2, w))),
        axis=0)


for i in range(0, N):
    wandb.log({"test_summary_image":
               [wandb.Image(gen_image()) for _ in range(IMG_COUNT)], "i": i}, step=i)
