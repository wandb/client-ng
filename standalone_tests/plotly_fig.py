import wandb
import plotly.graph_objs as go
import plotly.express as px

# This fails in plotly for python 2
# fig = go.Figure(go.Scatter(x=[0, 1, 2]))
fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
all_tests = {"plot": fig}

if __name__ == "__main__":
    wandb.init(project="plotly_test")
    wandb.log(all_tests)
