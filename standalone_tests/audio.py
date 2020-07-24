import numpy as np
import wandb

SAMPLE_N=100
audio_data = np.random.uniform(-1, 1, SAMPLE_N)

all_tests = {
    "audio-single": wandb.Audio('../tests/fixtures/piano.wav', sample_rate=24),
    "audio-seq": [ wandb.Audio('../tests/fixtures/piano.wav', sample_rate=24)],
    "audio-data": wandb.Audio(audio_data, sample_rate=SAMPLE_N),
    "audio-data-seq": [ wandb.Audio(audio_data, sample_rate=SAMPLE_N)]
}

if __name__ == "__main__":
    wandb.init(project='audio-test')
    for i in range(2):
        wandb.log(all_tests)
