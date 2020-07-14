import pytest
import time
import requests
from tests import utils
from multiprocessing import Process
from wandb import util
import click
from click.testing import CliRunner
import webbrowser


@pytest.fixture
def runner(monkeypatch, mocker):
    # whaaaaat = util.vendor_import("whaaaaat")
    # monkeypatch.setattr('wandb.cli.api', InternalApi(
    #    default_settings={'project': 'test', 'git_tag': True}, load_settings=False))
    monkeypatch.setattr(click, 'launch', lambda x: 1)
    # monkeypatch.setattr(whaaaaat, 'prompt', lambda x: {
    #                    'project_name': 'test_model', 'files': ['weights.h5'],
    #                    'attach': False, 'team_name': 'Manual Entry'})
    monkeypatch.setattr(webbrowser, 'open_new_tab', lambda x: True)
    return CliRunner()


def default_ctx():
    return {
        "fail_count": 0,
        "page_count": 0,
        "page_times": 2,
        "files": {},
    }


@pytest.fixture
def mock_server(mocker):
    from tests.mock_server import create_app
    ctx = default_ctx()
    app = create_app(ctx)
    mock = utils.RequestsMock(app, ctx)
    mocker.patch("gql.transport.requests.requests", mock)
    mocker.patch("wandb.internal.file_stream.requests", mock)
    mocker.patch("wandb.internal.internal_api.requests", mock)
    mocker.patch("wandb.internal.update.requests", mock)
    mocker.patch("wandb.apis.internal_runqueue.requests", mock)
    mocker.patch("wandb.apis.public.requests", mock)
    mocker.patch("wandb.util.requests", mock)
    mocker.patch("wandb.sdk.wandb_artifacts.requests", mock)
    return mock


@pytest.fixture
def live_mock_server(request):
    from tests.mock_server import create_app
    if request.node.get_closest_marker('port'):
        port = request.node.get_closest_marker('port').args[0]
    else:
        port = 8765
    app = create_app(default_ctx())
    server = Process(target=app.run, kwargs={"port": port, "debug": True,
                                             "use_reloader": False})
    server.start()
    for i in range(5):
        try:
            time.sleep(1)
            res = requests.get("http://localhost:%s/storage" % port, timeout=1)
            if res.status_code == 200:
                break
            print("Attempting to connect but got: %s", res)
        except requests.exceptions.RequestException:
            print("timed out")
    yield server
    server.terminate()
    server.join()
