import numpy as np
import wandb

wandb.init(project='audio-test')

SAMPLE_N=100
audio_data = np.random.uniform(-1, 1, SAMPLE_N)

all_tests = {
    "audio-single": wandb.Audio('../tests/fixtures/piano.wav', sample_rate=24),
    "audio-seq": [ wandb.Audio('../tests/fixtures/piano.wav', sample_rate=24)],
    "audio-data": wandb.Audio(audio_data, sample_rate=SAMPLE_N),
    "audio-data-seq": [ wandb.Audio(audio_data, sample_rate=SAMPLE_N)]
}

for i in range(2):
    wandb.log(all_tests)
