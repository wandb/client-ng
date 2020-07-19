import pytest
import time
import datetime
import os
import requests
from contextlib import contextmanager
from tests import utils
from multiprocessing import Process
import click
from click.testing import CliRunner
import webbrowser
import wandb
import git
import psutil
import atexit
from wandb.internal.git_repo import GitRepo
try:
    import nbformat
except ImportError:  # TODO: no fancy notebook fun in python2
    pass

try:
    from unittest.mock import MagicMock
except ImportError:  # TODO: this is only for python2
    from mock import MagicMock

DUMMY_API_KEY = '1824812581259009ca9981580f8f8a9012409eee'


def debug(*args, **kwargs):
    print("Open files during tests: ")
    proc = psutil.Process()
    print(proc.open_files())


atexit.register(debug)


@pytest.fixture
def git_repo(runner):
    with runner.isolated_filesystem():
        r = git.Repo.init(".")
        os.mkdir("wandb")
        # Because the forked process doesn't use my monkey patch above
        with open("wandb/settings", "w") as f:
            f.write("[default]\nproject: test")
        open("README", "wb").close()
        r.index.add(["README"])
        r.index.commit("Initial commit")
        yield GitRepo(lazy=False)


@pytest.fixture
def test_settings():
    """ Settings object for tests"""
    settings = wandb.Settings(_start_time=time.time(),
                              run_id=wandb.util.generate_id(),
                              _start_datetime=datetime.datetime.now())
    settings.files_dir = settings._path_convert(settings.files_dir_spec)
    return settings


@pytest.fixture
def mocked_run(runner, test_settings):
    """ A managed run object for tests with a mock backend """
    with runner.isolated_filesystem():
        run = wandb.wandb_sdk.wandb_run.RunManaged(settings=test_settings)
        run._set_backend(MagicMock())
        yield run


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
    mocker.patch('wandb.wandb_sdk.wandb_login.prompt',
                 lambda *args, **kwargs: DUMMY_API_KEY)
    return CliRunner()


@pytest.fixture(autouse=True)
def local_netrc(monkeypatch):
    """Never use our real credentials, put them in an isolated dir"""
    with CliRunner().isolated_filesystem():
        # TODO: this seems overkill...
        origexpand = os.path.expanduser

        def expand(path):
            return os.path.realpath("netrc") if "netrc" in path else origexpand(path)
        monkeypatch.setattr(os.path, "expanduser", expand)
        yield


@pytest.fixture
def mock_server():
    return utils.mock_server()


@pytest.fixture
def live_mock_server(request):
    port = utils.free_port()
    app = utils.create_app(utils.default_ctx())

    def worker(app, port):
        app.run(host="localhost", port=port, use_reloader=False, threaded=True)

    server = Process(target=worker, args=(app, port))
    server.base_url = "http://localhost:%s" % port
    server.start()
    for i in range(10):
        try:
            time.sleep(0.1)
            res = requests.get("%s/storage" % server.base_url, timeout=1)
            if res.status_code == 200:
                break
            print("Attempting to connect but got: %s", res)
        except requests.exceptions.RequestException:
            print("timed out")
    yield server
    server.terminate()
    server.join()


@pytest.fixture
def notebook(live_mock_server):
    @contextmanager
    def notebook_loader(nb_path, kernel_name="wandb_python", **kwargs):
        with open(utils.notebook_path("setup.ipynb")) as f:
            setupnb = nbformat.read(f, as_version=4)
            setupcell = setupnb['cells'][0]
            # Ensure the notebooks talks to our mock server
            new_source = setupcell['source'].replace("__WANDB_BASE_URL__",
                                                     live_mock_server.base_url)
            setupcell['source'] = new_source

        with open(utils.notebook_path(nb_path)) as f:
            nb = nbformat.read(f, as_version=4)
        nb['cells'].insert(0, setupcell)

        client = utils.WandbNotebookClient(nb)
        with client.setup_kernel(**kwargs):
            # Run setup commands for mocks
            client.execute_cell(0, store_history=False)
            yield client

    return notebook_loader


@pytest.fixture
def wandb_init_run(runner, mocker, mock_server, capsys):
    wandb._IS_INTERNAL_PROCESS = False
    mocker.patch('wandb.wandb_sdk.wandb_init.Backend', utils.BackendMock)
    run = wandb.init(settings=wandb.Settings(console="off", mode="offline"))
    yield run
    wandb.join()
