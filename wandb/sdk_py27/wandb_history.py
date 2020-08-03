# -*- coding: utf-8 -*-
"""History - Time series for Runs.

Track history from Run.log() calls.

"""

import time

from wandb.wandb_torch import TorchHistory


class History(object):
    """Time series data for Runs.
    """

    def __init__(self):
        self._step = 0
        self._data = dict()
        self._callback = None
        self._torch = None
        self._start_time = time.time()
        self.compute = True

    def _set_callback(self, cb):
        self._callback = cb

    def _row_update(self, row):
        self._data.update(row)

    def _row_add(self, row):
        self._data.update(row)
        self._flush()
        self._step += 1

    def _flush(self):
        if len(self._data) > 0:
            self._data["_step"] = self._step
            self._data["_runtime"] = int(
                self._data.get("_runtime", time.time() - self._start_time)
            )
            self._data["_timestamp"] = int(self._data.get("_timestamp", time.time()))
            if self._callback:
                self._callback(row=self._data, step=self._step)
            self._data = dict()

    def add(self, d):
        self._row_add(d)

    @property
    def torch(self):
        if self._torch is None:
            self._torch = TorchHistory(self)
        return self._torch
