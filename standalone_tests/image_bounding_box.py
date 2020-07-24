# Test for:
# - Semantic segmentation
import wandb
import random
from math import sin, cos, pi
import numpy as np

N = 12

IMG_SIZE = 400
image = np.random.randint(255, size=(IMG_SIZE, IMG_SIZE, 3))


def clamp(x, minmax):
    max(x, minmax[0], minmax[1])
class_id_to_label = {
    0: "car",
    1: "truck",
    2: "boat",
    3: "cthulhu",
    4: "tree",
    5: "store",
    6: "person",
    7: "bike",
    8: "motorcycle",
    9: "train"
}


# Generates an img with each box type that should all render the same
def balanced_corners_portrait():
    box_w = 40
    box_h = 20
    padding = 20
    img_width = 400
    img_height = 200
    image = np.random.randint(255, size=(img_height, img_width, 3))

    box_corners = [
        [padding, padding],
        [padding, img_height - box_h - padding],
        [img_width - box_w - padding, padding],
        [img_width -  box_w - padding, img_height - box_h - padding]]


    img_pixel = wandb.Image(image, boxes={
        "predctions": {
        "box_data": [
            {"position": {
                "middle": [x + box_w/2.0, y + box_h/2.0],
                "width":  box_w,
                "height":  box_h,
                },
            "class_id" : random.randint(0,10),
            "box_caption":  "m,w,h(pixel)",
            "scores" : {
                "acc": 0.7
                },
            "domain": "pixel"
            }
            for [x,y] in box_corners ],
        "class_labels": class_id_to_label
        }})

    img_norm_domain = wandb.Image(image, boxes={
        "predictions":
        {"box_data": [
            {"position": {
                "middle": [(x + box_w/2.0)/img_width, 
                           (y + box_h/2.0) / img_height],
                "width":  float(box_w) / img_width,
                "height":  float(box_h) / img_height,
                },
            "class_id" : random.randint(0,10),
            "box_caption": "m,w,h 0-1",
            "scores" : {
                "acc": 0.7
                }
            }
            for [x,y] in box_corners],
        "class_labels": class_id_to_label
    }})

    id = random.randint(0,10)
    img_min_max_pixel = wandb.Image(image, boxes={
        "predctions":
        {"box_data": [
            {"position": {
                "minX": x,
                "maxX": x + box_w,
                "minY": y,
                "maxY": y + box_h,
                },
            "class_id" : random.randint(0,10),
            "box_caption": "minMax(pixel)" ,
            "scores" : {
                "acc": 0.7
                },
            "domain": "pixel"
            }
            for [x,y] in box_corners],
        "class_labels": class_id_to_label
    }})

    img_min_max_norm_domain = wandb.Image(image, boxes={
        "predictions": {
            "box_data": [
                {"position": {
                    "minX": float(x)/img_width,
                    "maxX": float(x + box_w)/img_width,
                    "minY": float(y)/img_height,
                    "maxY": float(y + box_h)/img_height,
                    },
                    "class_id" : random.randint(0,10),
                    "box_caption": "minmax 0-1",
                    "scores" : {
                        "acc": 0.7
                        }
                    }
                for [x,y] in box_corners ],
            # "class_labels": class_id_to_label
        }})

    return [img_pixel, 
            img_norm_domain,
            img_min_max_pixel,
            img_min_max_norm_domain]

def all_tests():
    return {
        "balanced_corners_portrait": balanced_corners_portrait()[0],
        "balanced_corners_portrait_seq": balanced_corners_portrait(),
    }


if __name__ == "__main__":
    wandb.init(project="test-bounding-box")
    for i in range(N):
        wandb.log(all_tests)
