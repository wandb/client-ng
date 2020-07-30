import wandb
import plotly.graph_objs as go

all_tests = {"plot": go.Figure(go.Scatter(x=[0, 1, 2]))}

if __name__ == "__main__":
    wandb.init(project="plotly_test")
    wandb.log(all_tests)
