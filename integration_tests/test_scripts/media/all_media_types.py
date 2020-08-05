import numpy as np
import wandb

from . import image
from . import image_mask
from . import image_bounding_box
from . import video
from . import html
from . import table
from . import molecule
from . import point_cloud_scene
from . import object3D
# from . import plotly_fig
# from . import matplotlib_fig


IMG_WIDTH = 5
IMG_HEIGHT = 5

IMG_COUNT = 2
# Step coun
N = 3

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
# all_tests.update(plotly_fig.all_tests)
# all_tests.update(matplotlib_fig.all_tests)

if __name__ == "__main__":
    run_tests()

project_name ='all-media-test'

def run_tests():
    wandb.init(project=project_name)
    for _ in range(0, N):
        wandb.log(all_tests)

    run_path = project_name + "/" + wandb.run.id
    wandb.join()
    return run_path
