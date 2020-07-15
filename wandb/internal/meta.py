# -*- coding: utf-8 -*-
"""
meta.
"""

from datetime import datetime
import getpass
import json
import logging
import multiprocessing
import os
import platform
from shutil import copyfile
import socket
import sys

from wandb import _get_python_type, env, jupyter, util
from wandb.interface import interface
from wandb.internal import git_repo
from wandb.vendor.pynvml import pynvml


METADATA_FNAME = "wandb-metadata.json"

logger = logging.getLogger(__name__)


class Meta(object):
    """Used to store metadata during and after a run."""

    def __init__(self, settings=None, process_q=None, notify_q=None):
        self._settings = settings
        self.data = {}
        self.fname = os.path.join(self._settings.files_dir, METADATA_FNAME)
        self._interface = interface.BackendSender(
            process_queue=process_q, notify_queue=notify_q,
        )
        self._git = git_repo.GitRepo(
            remote=self._settings["git_remote"]
            if "git_remote" in self._settings.keys()
            else "origin"
        )

    def _save_code(self):
        if self._settings.code_program is None:
            logger.warn("unable to save code -- program entry not found")
            return

        root = self._git.root or os.getcwd()
        program_relative = self._settings.code_program
        util.mkdir_exists_ok(
            os.path.join(
                self._settings.files_dir, "code", os.path.dirname(program_relative)
            )
        )
        program_absolute = os.path.join(root, program_relative)
        saved_program = os.path.join(self._settings.files_dir, "code", program_relative)

        if not os.path.exists(saved_program):
            copyfile(program_absolute, saved_program)

    def _setup_sys(self):
        self.data["os"] = platform.platform(aliased=True)
        self.data["python"] = platform.python_version()
        self.data["args"] = sys.argv[1:]
        self.data["state"] = "running"
        self.data["heartbeatAt"] = datetime.utcnow().isoformat()
        self.data["startedAt"] = datetime.utcfromtimestamp(
            self._settings._start_time
        ).isoformat()

        if env.get_docker():
            self.data["docker"] = env.get_docker()
        try:
            pynvml.nvmlInit()
            self.data["gpu"] = pynvml.nvmlDeviceGetName(
                pynvml.nvmlDeviceGetHandleByIndex(0)
            ).decode("utf8")
            self.data["gpu_count"] = pynvml.nvmlDeviceGetCount()
        except pynvml.NVMLError:
            pass
        try:
            self.data["cpu_count"] = multiprocessing.cpu_count()
        except NotImplementedError:
            pass
        # TODO: we should use the cuda library to collect this
        if os.path.exists("/usr/local/cuda/version.txt"):
            with open("/usr/local/cuda/version.txt") as f:
                self.data["cuda"] = f.read().split(" ")[-1].strip()
        self.data["args"] = sys.argv[1:]
        self.data["state"] = "running"

    def _setup_git(self):
        if self._git.enabled:
            self.data["git"] = {
                "remote": self._git.remote_url,
                "commit": self._git.last_commit,
            }
            self.data["email"] = self._git.email
            self.data["root"] = self._git.root or self.data["root"] or os.getcwd()

    def probe(self):
        self._setup_sys()
        if not self._settings.disable_code:
            if self._settings.code_program is not None:
                self.data["codePath"] = self._settings.code_program
                self.data["program"] = os.path.basename(self._settings.code_program)
            else:
                self.data["program"] = "<python with no main file>"
                if _get_python_type() != "python":
                    if os.getenv(env.NOTEBOOK_NAME):
                        self.data["program"] = os.getenv(env.NOTEBOOK_NAME)
                    else:
                        meta = jupyter.notebook_metadata()
                        if meta.get("path"):
                            if "fileId=" in meta["path"]:
                                self.data["colab"] = (
                                    "https://colab.research.google.com/drive/"
                                    + meta["path"].split("fileId=")[1] # noqa
                                )
                                self.data["program"] = meta["name"]
                            else:
                                self.data["program"] = meta["path"]
                                self.data["root"] = meta["root"]
            self._setup_git()

        try:
            username = getpass.getuser()
        except KeyError:
            # getuser() could raise KeyError in restricted environments like
            # chroot jails or docker containers.  Return user id in these cases.
            username = str(os.getuid())

        if self.settings().get("anonymous") != "true":
            self.data["host"] = os.environ.get(env.HOST, socket.gethostname())
            self.data["username"] = os.getenv(env.USERNAME, username)
            self.data["executable"] = sys.executable
        else:
            self.data.pop("email", None)
            self.data.pop("root", None)

        if self._settings.save_code:
            self._save_code()

    def write(self):
        with open(self.fname, "w") as f:
            s = json.dumps(self.data, indent=4)
            f.write(s)
            f.write("\n")
        base_name = os.path.basename(self.fname)
        files = dict(files=[(base_name,)])

        if "codePath" in self.data:
            code_bname = os.path.basename(self.data["codePath"])
            files["files"].append((code_bname,))

        self._interface.send_files(files)
