from wandb.cli import cli
import contextlib
import traceback
import platform
import pytest
import netrc
import os

DUMMY_API_KEY = '1824812581259009ca9981580f8f8a9012409eee'


@pytest.fixture
def empty_netrc(monkeypatch):
    class FakeNet(object):
        @property
        def hosts(self):
            return {'api.wandb.ai': None}
    monkeypatch.setattr(netrc, "netrc", lambda *args: FakeNet())


@contextlib.contextmanager
def config_dir():
    try:
        os.environ["WANDB_CONFIG"] = os.getcwd()
        yield
    finally:
        del os.environ["WANDB_CONFIG"]


def test_init_reinit(runner, empty_netrc, local_netrc, mock_server):
    with runner.isolated_filesystem():
        runner.invoke(cli.login, [DUMMY_API_KEY])
        result = runner.invoke(cli.init, input="y\nvanpelt\n")
        print(result.output)
        print(result.exception)
        print(traceback.print_tb(result.exc_info[2]))
        assert result.exit_code == 0
        with open("netrc", "r") as f:
            generatedNetrc = f.read()
        with open("wandb/settings", "r") as f:
            generatedWandb = f.read()
        assert DUMMY_API_KEY in generatedNetrc
        assert "vanpelt" in generatedWandb


def test_init_add_login(runner, empty_netrc, mock_server):
    with runner.isolated_filesystem():
        with config_dir():
            with open("netrc", "w") as f:
                f.write("previous config")
            runner.invoke(cli.login, [DUMMY_API_KEY])
            result = runner.invoke(cli.init, input="y\n%s\nvanpelt\n" % DUMMY_API_KEY)
            print(result.output)
            print(result.exception)
            print(traceback.print_tb(result.exc_info[2]))
            assert result.exit_code == 0
            with open("netrc", "r") as f:
                generatedNetrc = f.read()
            with open("wandb/settings", "r") as f:
                generatedWandb = f.read()
            assert DUMMY_API_KEY in generatedNetrc
            assert "base_url" in generatedWandb


def test_init_existing_login(runner, mock_server):
    with runner.isolated_filesystem():
        with open("netrc", "w") as f:
            f.write("machine api.wandb.ai\n\tlogin test\tpassword 12345")
        result = runner.invoke(cli.init, input="vanpelt\nfoo\n")
        print(result.output)
        print(result.exception)
        print(traceback.print_tb(result.exc_info[2]))
        assert result.exit_code == 0
        with open("wandb/settings", "r") as f:
            generatedWandb = f.read()
        assert "vanpelt" in generatedWandb
        assert "This directory is configured" in result.output


@pytest.mark.skip(reason="Currently dont have on in cling")
def test_enable_on(runner, git_repo):
    with open("wandb/settings", "w") as f:
        f.write("[default]\nproject=rad")
    result = runner.invoke(cli.on)
    print(result.output)
    print(result.exception)
    print(traceback.print_tb(result.exc_info[2]))
    assert "W&B enabled" in str(result.output)
    assert result.exit_code == 0


@pytest.mark.skip(reason="Currently dont have off in cling")
def test_enable_off(runner, git_repo):
    with open("wandb/settings", "w") as f:
        f.write("[default]\nproject=rad")
    result = runner.invoke(cli.off)
    print(result.output)
    print(result.exception)
    print(traceback.print_tb(result.exc_info[2]))
    assert "W&B disabled" in str(result.output)
    assert "disabled" in open("wandb/settings").read()
    assert result.exit_code == 0


def test_artifact_download(runner, git_repo, mock_server):
    result = runner.invoke(cli.artifact, ["get", "test/mnist:v0"])
    print(result.output)
    print(result.exception)
    print(traceback.print_tb(result.exc_info[2]))
    assert result.exit_code == 0
    assert "Downloading dataset artifact" in result.output
    path = os.path.join(".", "artifacts", "mnist:v0")
    if platform.system() == "Windows":
        path = path.replace(":", "-")
    assert "Artifact downloaded to %s" % path in result.output
    assert os.path.exists(path)


def test_artifact_upload(runner, git_repo, mock_server, mocker, mocked_run):
    with open("artifact.txt", "w") as f:
        f.write("My Artifact")
    mocker.patch('wandb.init', lambda *args, **kwargs: mocked_run)
    result = runner.invoke(cli.artifact, ["put", "artifact.txt", "-n", "test/simple"])
    print(result.output)
    print(result.exception)
    print(traceback.print_tb(result.exc_info[2]))
    assert result.exit_code == 0
    assert "Uploading file artifact.txt to:" in result.output
    #  TODO: one of the tests above is setting entity to y
    assert 'test/simple:v0' in result.output


def test_artifact_ls(runner, git_repo, mock_server):
    result = runner.invoke(cli.artifact, ["ls", "test"])
    print(result.output)
    print(result.exception)
    print(traceback.print_tb(result.exc_info[2]))
    assert result.exit_code == 0
    assert "9KB" in result.output
    assert "mnist:v2" in result.output