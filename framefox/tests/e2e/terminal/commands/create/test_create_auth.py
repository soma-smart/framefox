import subprocess
import pytest
import os
import yaml

from framefox.tests.e2e.fixtures.commands import TMP_PATH, handle_tmp_path, init_project, exec_command


@pytest.fixture
def create_user(init_project):
    result = exec_command(
        ["framefox", "create", "user"],
        input_value="user\n"
    )

    assert result.returncode == 0, f"User creation failed with error: {result.stderr.strip()}"


def test_create_auth_command_should_exist(init_project):
    result = exec_command(["framefox", "create", "auth", "--help"])

    assert result.returncode == 0, f"Command failed with error: {result.stderr.strip()}"


def test_create_auth_command_without_input_should_fail(init_project):
    result = exec_command(["framefox", "create", "auth"])

    assert result.returncode != 0, "Command should fail without input"


def test_create_auth_command_without_user_before_should_fail(init_project):
    result = exec_command(
        ["framefox", "create", "auth"],
        input_value="1\n\nuser\n"
    )

    assert result.returncode != 0, f"Command should fail without user before input"


@pytest.mark.parametrize("user_input", ["\n\n\n", "1\n\n\n", "1\n\nuser\n", "1\nauth\n\n"])
def test_create_auth_command_with_user_before_should_succeed(user_input, create_user, init_project):
    result = exec_command(
        ["framefox", "create", "auth"],
        input_value=user_input
    )

    assert result.returncode == 0, f"Command should succeed with user before input"


def test_create_auth_command_should_create_authenticator_file(create_user, init_project):
    files = ["src/security/default_authenticator.py", "src/controller/login_controller.py", "templates/security/login.html", "config/security.yaml"]

    exec_command(
        ["framefox", "create", "auth"],
        input_value="\n\n\n"
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


def test_create_auth_command_when_already_done_should_fail(create_user, init_project):
    exec_command(
        ["framefox", "create", "auth"],
        input_value="\n\n\n"
    )

    result = exec_command(
        ["framefox", "create", "auth"],
        input_value="\n\n\n"
    )

    assert result.returncode != 0, "Command should fail if authenticator already exists"