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

all_tests = {}
all_tests.update(image.all_tests)
all_tests.update(image_mask.all_tests)
all_tests.update(image_bounding_boxes.all_tests)
all_tests.update(video.all_tests)
all_tests.update(molecule.all_tests)
all_tests.update(point_cloud_scene.all_tests)
all_tests.update(object3D.all_tests)

for i in range(0, N):
    if i % M == 0:
        wandb.log(all_tests)
