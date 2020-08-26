FROM circleci/python:3.7

RUN sudo apt-get update && sudo apt-get install -y libsndfile1 ffmpeg
COPY requirements.txt requirements_test.txt
COPY requirements_main.txt requirements_wandb.txt
RUN pip install -r requirements_test.txt
RUN pip install -r requirements_wandb.txt
