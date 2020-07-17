import requests
import json
import os
import wandb
from wandb.interface import interface
from tests.mock_server import create_app
from _pytest.config import get_config  # type: ignore
from pytest_mock import _get_mock_module  # type: ignore


def subdict(d, expected_dict):
    """Return a new dict with only the items from `d` whose keys occur in `expected_dict`.
    """
    return {k: v for k, v in d.items() if k in expected_dict}


def fixture_open(path):
    """Returns an opened fixture file"""
    return open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "fixtures", path))


def default_ctx():
    return {
        "fail_count": 0,
        "page_count": 0,
        "page_times": 2,
        "files": {},
    }


def mock_server():
    ctx = default_ctx()
    app = create_app(ctx)
    mock = RequestsMock(app, ctx)
    mocker = _get_mock_module(get_config())
    # We mock out all requests libraries, couldn't find a way to mock the core lib
    mocker.patch("gql.transport.requests.requests", mock).start()
    mocker.patch("wandb.internal.file_stream.requests", mock).start()
    mocker.patch("wandb.internal.internal_api.requests", mock).start()
    mocker.patch("wandb.internal.update.requests", mock).start()
    mocker.patch("wandb.apis.internal_runqueue.requests", mock).start()
    mocker.patch("wandb.apis.public.requests", mock).start()
    mocker.patch("wandb.util.requests", mock).start()
    mocker.patch("wandb.wandb_sdk.wandb_artifacts.requests", mock).start()
    print("Patched requests everywhere", os.getpid())
    return mock


class ResponseMock(object):
    def __init__(self, response):
        self.response = response

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def raise_for_status(self):
        if self.response.status_code >= 400:
            raise requests.exceptions.HTTPError("Bad Request", response=self.response)

    @property
    def content(self):
        return self.response.data.decode('utf-8')

    @property
    def headers(self):
        return self.response.headers

    def iter_content(self, chunk_size=1024):
        yield self.response.data

    def json(self):
        return json.loads(self.response.data.decode('utf-8'))


class RequestsMock(object):
    def __init__(self, app, ctx):
        self.app = app
        self.client = app.test_client()
        self.ctx = ctx

    def set_context(self, key, value):
        self.ctx[key] = value

    def Session(self):
        return self

    @property
    def RequestException(self):
        return requests.RequestException

    @property
    def HTTPError(self):
        return requests.HTTPError

    @property
    def headers(self):
        return {}

    @property
    def utils(self):
        return requests.utils

    @property
    def exceptions(self):
        return requests.exceptions

    @property
    def packages(self):
        return requests.packages

    @property
    def adapters(self):
        return requests.adapters

    def mount(self, *args):
        pass

    def _clean_kwargs(self, kwargs):
        if "auth" in kwargs:
            del kwargs["auth"]
        if "timeout" in kwargs:
            del kwargs["timeout"]
        if "cookies" in kwargs:
            del kwargs["cookies"]
        if "params" in kwargs:
            del kwargs["params"]
        if "stream" in kwargs:
            del kwargs["stream"]
        if "verify" in kwargs:
            del kwargs["verify"]
        if "allow_redirects" in kwargs:
            del kwargs["allow_redirects"]
        return kwargs

    def _store_request(self, url, body):
        key = url.split("/")[-1]
        self.ctx[key] = self.ctx.get(key, [])
        self.ctx[key].append(body)

    def post(self, url, **kwargs):
        self._store_request(url, kwargs.get("json"))
        return ResponseMock(self.client.post(url, **self._clean_kwargs(kwargs)))

    def put(self, url, **kwargs):
        self._store_request(url, kwargs.get("json"))
        return ResponseMock(self.client.put(url, **self._clean_kwargs(kwargs)))

    def get(self, url, **kwargs):
        self._store_request(url, kwargs.get("json"))
        return ResponseMock(self.client.get(url, **self._clean_kwargs(kwargs)))

    def request(self, method, url, **kwargs):
        if method.lower() == "get":
            self.get(url, **kwargs)
        elif method.lower() == "post":
            self.post(url, **kwargs)
        elif method.lower() == "put":
            self.put(url, **kwargs)
        else:
            message = "Request method not implemented: %s" % method
            raise requests.RequestException(message)

    def __repr__(self):
        return "<W&B Mocked Request class>"


class ProcessMock(object):
    def __init__(self, *args, **kwargs):
        self.pid = 0
        self.name = "wandb_internal"
        self.daemon = True
        self._is_alive = True
        self.exitcode = 0

    def is_alive(self):
        return self._is_alive

    def start(self):
        pass

    def join(self, *args):
        self.is_alive = False

    def kill(self):
        self.is_alive = False

    def terminate(self):
        self.is_alive = False

    def close(self):
        self.is_alive = False


class BackendMock(object):
    def __init__(self, mode=None):
        self.calls = {}
        self._run = None
        self._done = True
        self._wl = wandb.setup()
        self.process_queue = self._wl._multiprocessing.Queue()
        self.req_queue = self._wl._multiprocessing.Queue()
        self.resp_queue = self._wl._multiprocessing.Queue()
        self.cancel_queue = self._wl._multiprocessing.Queue()
        self.notify_queue = self._wl._multiprocessing.Queue()
        self.interface = None
        self.last_queued = None
        self.history = []
        self.summary = {}
        self.config = {}
        self.files = []
        self.mocker = _get_mock_module(get_config())

    def _hack_set_run(self, run):
        self._run = run
        self.interface._hack_set_run(run)

    def _request_response(self, rec, timeout=5):
        return rec

    def _proto_to_dict(self, obj_list):
        d = dict()
        for item in obj_list:
            d[item.key] = json.loads(item.value_json)
        return d

    def _queue_process(self, rec):
        if len(rec.history.item) > 0:
            hist = self._proto_to_dict(rec.history.item)
            self.history.append(hist)
        if len(rec.summary.update) > 0:
            self.summary.update(self._proto_to_dict(rec.summary.update))
        if len(rec.files.files) > 0:
            self.files.append([f.path for f in rec.files.files])
        if rec.run:
            pass

        self.last_queued = rec
        self.interface._orig_queue_process(rec)

    def ensure_launched(self, *args, **kwargs):
        print("Fake Backend Launched")
        wandb_process = ProcessMock()
        self.interface = interface.BackendSender(
            process=wandb_process,
            notify_queue=self.notify_queue,
            process_queue=self.process_queue,
            request_queue=self.req_queue,
            response_queue=self.resp_queue,
        )
        self.interface._request_response = self._request_response
        self.interface._orig_queue_process = self.interface._queue_process
        self.interface._queue_process = self._queue_process

    def server_connect(self):
        pass

    def server_status(self):
        pass

    def cleanup(self):
        pass
