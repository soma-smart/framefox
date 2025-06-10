import subprocess
import shutil
import pytest
import os
import yaml


TMP_PATH = "test_dir"


@pytest.fixture(autouse=True)
def init_project():
    if os.path.exists(TMP_PATH):
        shutil.rmtree(TMP_PATH)

    os.mkdir(TMP_PATH)
    result = subprocess.run(
        ["framefox", "init"],
        cwd=TMP_PATH,
        capture_output=True,
        text=True
    )

    yield
    if os.path.exists(TMP_PATH):
        shutil.rmtree(TMP_PATH)


@pytest.fixture
def create_user(init_project):
    result = subprocess.run(
        ["framefox", "create", "user"],
        cwd=TMP_PATH,
        input="user\n",
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"User creation failed with error: {result.stderr.strip()}"


def test_create_auth_command_should_exist():
    result = subprocess.run(
        ["framefox", "create", "auth", "--help"],
        cwd=TMP_PATH,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Command failed with error: {result.stderr.strip()}"


def test_create_auth_command_without_input_should_fail():
    result = subprocess.run(
        ["framefox", "create", "auth"],
        cwd=TMP_PATH,
        capture_output=True,
        text=True
    )

    assert result.returncode != 0, "Command should fail without input"


def test_create_auth_command_without_user_before_should_fail(init_project):
    result = subprocess.run(
        ["framefox", "create", "auth"],
        cwd=TMP_PATH,
        input="1\n\nuser\n",
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0, f"Command should fail without user before input"


@pytest.mark.parametrize("user_input", ["\n\n\n", "1\n\n\n", "1\n\nuser\n", "1\nauth\n\n"])
def test_create_auth_command_with_user_before_should_succeed(user_input, init_project, create_user):
    result = subprocess.run(
        ["framefox", "create", "auth"],
        cwd=TMP_PATH,
        input=user_input,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Command should succeed with user before input"


def test_create_auth_command_should_create_authenticator_file(init_project, create_user):
    files = ["src/security/default_authenticator.py", "src/controllers/login_controller.py", "templates/security/login.html", "config/security.yaml"]

    subprocess.run(
        ["framefox", "create", "auth"],
        cwd=TMP_PATH,
        input="\n\n\n",
        capture_output=True,
        text=True,
    )

    for file in files:
        assert os.path.exists(os.path.join(TMP_PATH, file)), f"File {file} was not created"

    with open(os.path.join(TMP_PATH, "config/security.yaml"), "r") as f:
        config = yaml.safe_load(f)

    providers = config.get("security", {}).get("providers", {})
    app_user_provider = providers.get("app_user_provider", {})
    entity = app_user_provider.get("entity", {})

    firewalls = config.get("security", {}).get("firewalls", {})
    main = firewalls.get("main", {})

    assert entity.get("class") == "src.entity.user.User", "Incorrect entity class in security.yaml"
    assert main.get("provider") == "app_user_provider", "Incorrect provider in firewalls.main in security.yaml"


def test_create_auth_command_when_already_done_should_fail(init_project, create_user):
    subprocess.run(
        ["framefox", "create", "auth"],
        cwd=TMP_PATH,
        input="\n\n\n",
        capture_output=True,
        text=True,
    )

    result = subprocess.run(
        ["framefox", "create", "auth"],
        cwd=TMP_PATH,
        input="\n\n\n",
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0, "Command should fail if authenticator already exists"