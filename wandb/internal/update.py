from pkg_resources import parse_version
import requests
import wandb
import threading
from wandb.internal import internal_util


class _Future(object):
    def __init__(self):
        self._object = None
        self._object_ready = threading.Event()
        self._lock = threading.Lock()

    def get(self, timeout=None):
        is_set = self._object_ready.wait(timeout)
        if is_set:
            if self._object:
                return self._object
            if self._except:
                raise self._except
        return None

    def _set_object(self, obj):
        self._object = obj
        self._object_ready.set()

    def _set_exception(self, exc):
        self._except = exc
        self._object_ready.set()


class AsyncCall(threading.Thread):
    def __init__(func):
        self._func = func
        self._future = _Future()
        self.start()
        return self._future

    def run(self):
        try:
            ret = self._func()
        except Exception as e:
            self._future._set_exception(e)
        else:
            self._future._set_object(ret)


def _find_available(current_version):
    timeout = 2  # Two seconds.
    pypi_url = "https://pypi.org/pypi/%s/json" % wandb._wandb_module
    request_thread = RequestURLThread(pypi_url, timeout=timeout)
    request_thread.start()
    async_call = AsyncCall(lambda: requests.get(pypi_url, timeout=timeout).json())

    try:
        async_requests_get = AsyncCall(requests.get)
        task = async_requests_get(pypi_url, timeout=timeout)
        task.wait()
        if task.done():
            data = task.result()
        data = requests.get(pypi_url, timeout=timeout).json()
        latest_version = data["info"]["version"]
        release_list = data["releases"].keys()
    except Exception:
        # Any issues whatsoever, just skip the latest version check.
        return

    # Return if no update is available
    pip_prerelease = False
    parsed_current_version = parse_version(current_version)
    if parse_version(latest_version) <= parsed_current_version:
        # pre-releases are not included in latest_version
        # so if we are currently running a pre-release we check more
        if not parsed_current_version.is_prerelease:
            return
        # Candidates are pre-releases with the same base_version
        release_list = map(parse_version, release_list)
        release_list = filter(lambda v: v.is_prerelease, release_list)
        release_list = filter(
            lambda v: v.base_version == parsed_current_version.base_version,
            release_list,
        )
        release_list = sorted(release_list)
        if not release_list:
            return
        parsed_latest_version = release_list[-1]
        if parsed_latest_version <= parsed_current_version:
            return
        latest_version = str(parsed_latest_version)
        pip_prerelease = True

    return (latest_version, pip_prerelease)


def check_available(current_version):
    package_info = _find_available(current_version)
    if not package_info:
        return

    latest_version, pip_prerelease = package_info

    # A new version is available!
    return (
        "%s version %s is available!  To upgrade, please run:\n"
        " $ pip install %s --upgrade%s"
        % (
            wandb._wandb_module,
            latest_version,
            wandb._wandb_module,
            " --pre" if pip_prerelease else "",
        )
    )
