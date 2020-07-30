import numpy as np
import wandb

import image
import image_mask
import image_bounding_box
import video
import html
import table
import molecule
import point_cloud_scene
import object3D

wandb.init(project='all-media-test')


IMG_WIDTH = 5
IMG_HEIGHT = 5

IMG_COUNT = 2
# Step coun
N = 3


def gen_image(w=IMG_WIDTH, h=IMG_HEIGHT):
    return np.concatenate(
        (np.random.rand(h//2, w),
         np.zeros((h//2, w))),
        axis=0)

all_tests = {}
all_tests.update(image.all_tests)
all_tests.update(image_mask.all_tests)
all_tests.update(image_bounding_box.all_tests)
all_tests.update(video.all_tests)
all_tests.update(html.all_tests)
all_tests.update(table.all_tests)
all_tests.update(molecule.all_tests)
all_tests.update(point_cloud_scene.all_tests)
all_tests.update(object3D.all_tests)

for i in range(0, N):
    wandb.log(all_tests)
