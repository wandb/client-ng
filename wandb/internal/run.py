# -*- coding: utf-8 -*-
"""InternalRun - Internal-only run object.

Semi-stubbed run for internal process use.

"""
from wandb import data_types
from wandb.wandb_sdk import wandb_run  # type: ignore[import]


class InternalRun(wandb_run.RunManaged):
    def __init__(self, run_obj, settings):
        super(InternalRun, self).__init__(settings=settings)
        self._run_obj = run_obj

        # TODO: This undoes what's done in the constructor of RunManaged. Probably what
        # really want is a common interface for RunManaged and InternalRun.
        data_types._datatypes_set_callback(None)

    def _set_backend(self, backend):
        # This type of run object can't have a backend
        # or do any writes.
        pass
