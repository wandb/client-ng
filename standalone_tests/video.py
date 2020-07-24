import numpy as np
import wandb

N = 1
M = 2


all_tests = {
    "test_video": wandb.Video("../tests/fixtures/video1.mp4", caption="Cool"),
    "test_video_seq": [wandb.Video("../tests/fixtures/video1.mp4", caption="Cool")],
    "test_video_data": wandb.Video(np.random.random(size=(1, 5, 3, 28, 28)))
}

if __name__ == "__main__":
    wandb.init(project="video-test")
    for i in range(N):
        wandb.log(all_tests)
