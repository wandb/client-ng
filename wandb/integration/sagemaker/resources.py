import json
import os
import socket


def parse_sm_resources():
    run_dict = dict()
    env_dict = dict()
    run_id = os.getenv("TRAINING_JOB_NAME")
    if run_id:
        run_dict["run_id"] = "-".join(
            [run_id, os.getenv("CURRENT_HOST", socket.gethostname())]
        )
    conf = json.load(open("/opt/ml/input/config/resourceconfig.json"))
    if len(conf["hosts"]) > 1:
        run_dict["group"] = os.getenv("TRAINING_JOB_NAME")
    # Set secret variables
    if os.path.exists("secrets.env"):
        for line in open("secrets.env", "r"):
            key, val = line.strip().split("=", 1)
            env_dict[key] = val
    return run_dict, env_dict
