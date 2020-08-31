import json
import os
import re

import six


def parse_sm_config():
    """Attempts to parse SageMaker configuration returning False if it can't find it"""
    sagemaker_config = "/opt/ml/input/config/hyperparameters.json"
    resource_config = "/opt/ml/input/config/resourceconfig.json"
    if os.path.exists(sagemaker_config) and os.path.exists(resource_config):
        conf = {}
        conf["sagemaker_training_job_name"] = os.getenv("TRAINING_JOB_NAME")
        # Hyper-parameter searchs quote configs...
        for k, v in six.iteritems(json.load(open(sagemaker_config))):
            cast = v.strip('"')
            if os.getenv("WANDB_API_KEY") is None and k == "wandb_api_key":
                os.environ["WANDB_API_KEY"] = cast
            else:
                if re.match(r"^[-\d]+$", cast):
                    cast = int(cast)
                elif re.match(r"^[-.\d]+$", cast):
                    cast = float(cast)
                conf[k] = cast
        return conf
    else:
        return False
