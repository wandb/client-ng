import matplotlib.pyplot as plt
import numpy as np
import wandb


plot_x = [5, 50, 60, 75, 90]
plot_y1 = [0.0, 0.003546099178493023, 0.0036275694146752357,
           0.007858546450734138, 0.017621144652366638]
plot_y2 = [0.0016313214, 0.0, 0.009852217, 0.014705882, 0.0125]

plt.clf()
plt.plot(plot_x, plot_y1, label="y1")

all_tests = {"name": plt}

N = 2
if __name__ == "__main__":
    wandb.init(project='matplotlib-test')
    wandb.log(all_tests)

