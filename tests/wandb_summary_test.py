"""
settings test.
"""

import pytest  # type: ignore

from wandb import wandb_sdk


class MockCallback(object):
    def __init__(self):
        self._dict = {}
        self.reset()

    def reset(self):
        self.key = None
        self.val = None
        self.data = None

    def callback(self, key=None, val=None, data=None):
        self.key = key
        self.val = val
        self.data = data

    def check(self, key=None, val=None, data=None):
        if key:
            assert self.key == key
        if val:
            assert self.val == val
        if data:
            assert self.data == data
        return self


def test_attrib_get():
    s = wandb_sdk.Summary()
    s['this'] = 2
    assert s.this == 2


def test_item_get():
    s = wandb_sdk.Summary()
    s['this'] = 2
    assert s['this'] == 2


def test_cb_attrib():
    m = MockCallback()
    s = wandb_sdk.Summary()
    s._set_callback(m.callback)
    s.this = 2
    m.check(key='this', val=2, data=dict(this=2))

def test_cb_item():
    m = MockCallback()
    s = wandb_sdk.Summary()
    s._set_callback(m.callback)
    s['this'] = 2
    m.check(key='this', val=2, data=dict(this=2))

def test_cb_item_nested():
    m = MockCallback()
    s = wandb_sdk.Summary()
    s._set_callback(m.callback)
    s['this'] = 2
    m.check(key='this', val=2, data=dict(this=2)).reset()

    s['that'] = dict(nest1=dict(nest2=4, nest2b=5))
    m.check(key='that', val=dict(nest1=dict(nest2=4, nest2b=5)), data=dict(this=2, that=dict(nest1=dict(nest2=4, nest2b=5)))).reset()

    s['that']["nest1"]["nest2"] = 3
    m.check(key=('that', "nest1", "nest2"), val=3, data=dict(this=2, that=dict(nest1=dict(nest2=3, nest2b=5)))).reset()

    s['that']["nest1"] = 8
    m.check(key=('that', "nest1"), val=8, data=dict(this=2, that=dict(nest1=8))).reset()

    s['that']["nest1a"] = dict(nest2c=9)
    m.check(key=('that', "nest1a"), val=dict(nest2c=9), data=dict(this=2, that=dict(nest1=8, nest1a=dict(nest2c=9)))).reset()
