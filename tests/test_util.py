import random

import numpy
import tensorflow
import torch

from . import utils
from wandb import util


def pt_variable(nested_list, requires_grad=True):
    v = torch.autograd.Variable(torch.Tensor(nested_list))
    v.requires_grad = requires_grad
    return v


def r():
    return random.random()


def nested_list(*shape):
    """Makes a nested list of lists with a "shape" argument like numpy,
    TensorFlow, etc.
    """
    if not shape:
        # reduce precision so we can use == for comparison regardless
        # of conversions between other libraries
        return [float(numpy.float16(random.random()))]
    else:
        return [nested_list(*shape[1:]) for _ in range(shape[0])]


def json_friendly_test(orig_data, obj):
    data, converted = util.json_friendly(obj)
    utils.assert_deep_lists_equal(orig_data, data)
    assert converted


def tensorflow_json_friendly_test(orig_data):
    json_friendly_test(
        orig_data, tensorflow.convert_to_tensor(orig_data))
    v = tensorflow.Variable(tensorflow.convert_to_tensor(orig_data))
    json_friendly_test(orig_data, v)


def test_pytorch_json_0d():
    a = nested_list()
    json_friendly_test(a, torch.Tensor(a))
    json_friendly_test(a, pt_variable(a))


def test_pytorch_json_1d_1x1():
    a = nested_list(1)
    json_friendly_test(a, torch.Tensor(a))
    json_friendly_test(a, pt_variable(a))


def test_pytorch_json_1d():
    a = nested_list(3)
    json_friendly_test(a, torch.Tensor(a))
    json_friendly_test(a, pt_variable(a))


def test_pytorch_json_1d_large():
    a = nested_list(300)
    json_friendly_test(a, torch.Tensor(a))
    json_friendly_test(a, pt_variable(a))


def test_pytorch_json_2d():
    a = nested_list(3, 3)
    json_friendly_test(a, torch.Tensor(a))
    json_friendly_test(a, pt_variable(a))


def test_pytorch_json_2d_large():
    a = nested_list(300, 300)
    json_friendly_test(a, torch.Tensor(a))
    json_friendly_test(a, pt_variable(a))


def test_pytorch_json_3d():
    a = nested_list(3, 3, 3)
    json_friendly_test(a, torch.Tensor(a))
    json_friendly_test(a, pt_variable(a))


def test_pytorch_json_4d():
    a = nested_list(1, 1, 1, 1)
    json_friendly_test(a, torch.Tensor(a))
    json_friendly_test(a, pt_variable(a))


def test_pytorch_json_nd():
    a = nested_list(1, 1, 1, 1, 1, 1, 1, 1)
    json_friendly_test(a, torch.Tensor(a))
    json_friendly_test(a, pt_variable(a))


def test_pytorch_json_nd_large():
    a = nested_list(3, 3, 3, 3, 3, 3, 3, 3)
    json_friendly_test(a, torch.Tensor(a))
    json_friendly_test(a, pt_variable(a))


def test_tensorflow_json_0d():
    tensorflow_json_friendly_test(nested_list())


def test_tensorflow_json_1d_1x1():
    tensorflow_json_friendly_test(nested_list(1))


def test_tensorflow_json_1d():
    tensorflow_json_friendly_test(nested_list(3))


def test_tensorflow_json_1d_large():
    tensorflow_json_friendly_test(nested_list(300))


def test_tensorflow_json_2d():
    tensorflow_json_friendly_test(nested_list(3, 3))


def test_tensorflow_json_2d_large():
    tensorflow_json_friendly_test(nested_list(300, 300))


def test_tensorflow_json_nd():
    tensorflow_json_friendly_test(nested_list(1, 1, 1, 1, 1, 1, 1, 1))


def test_tensorflow_json_nd_large():
    tensorflow_json_friendly_test(nested_list(3, 3, 3, 3, 3, 3, 3, 3))


def test_image_from_docker_args_simple():
    image = util.image_from_docker_args([
        "run", "-v", "/foo:/bar", "-e", "NICE=foo", "-it", "wandb/deepo", "/bin/bash"])
    assert image == "wandb/deepo"


def test_image_from_docker_args_simple_no_namespace():
    image = util.image_from_docker_args([
        "run", "-e", "NICE=foo", "nginx", "/bin/bash"])
    assert image == "nginx"


def test_image_from_docker_args_simple_no_equals():
    image = util.image_from_docker_args([
        "run", "--runtime=runc", "ufoym/deepo:cpu-all"])
    assert image == "ufoym/deepo:cpu-all"


def test_image_from_docker_args_bash_simple():
    image = util.image_from_docker_args([
        "run", "ufoym/deepo:cpu-all", "/bin/bash", "-c", "python train.py"])
    assert image == "ufoym/deepo:cpu-all"


def test_image_from_docker_args_sha():
    dsha = ("wandb/deepo@sha256:"
            "3ddd2547d83a056804cac6aac48d46c5394a76df76b672539c4d2476eba38177")
    image = util.image_from_docker_args([dsha])
    assert image == dsha