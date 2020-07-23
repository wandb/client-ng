import numpy as np
import wandb

import image
import image_mask
import video
import molecule
import point_cloud_scene
import object3D

wandb.init(project='image-test')


IMG_WIDTH = 5
IMG_HEIGHT = 5

IMG_COUNT = 2
# Step count
N = 10
# Log frequency
M = 1


def gen_image(w=IMG_WIDTH, h=IMG_HEIGHT):
    return np.concatenate(
        (np.random.rand(h//2, w),
         np.zeros((h//2, w))),
        axis=0)

all_tests = {
    **image.all_tests,
    **image_mask.all_tests,
    **video.all_tests,
    **molecule.all_tests,
    **point_cloud_scene.all_tests,
    **object3D.all_tests
}



for i in range(0, N):
    if i % M == 0:
        wandb.log(all_tests)

import time
time.sleep(1000)
