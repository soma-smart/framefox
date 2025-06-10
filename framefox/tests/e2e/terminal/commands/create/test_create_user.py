import pytest
import os
import subprocess

from framefox.tests.e2e.fixtures.commands import TMP_PATH, handle_tmp_path, init_project, exec_command


def test_create_user_command_should_exist(init_project):
    result = exec_command(["framefox", "create", "user", "--help"])

    assert result.returncode == 0, f"Command failed with error: {result.stderr.strip()}"


def test_create_user_command_without_input_should_fail(init_project):
    result = exec_command(["framefox", "create", "user"])

    assert result.returncode != 0, "Command should fail without input"


@pytest.mark.parametrize("input_value", ["\n", "user\n"])
def test_create_user_command_with_valid_input_should_succeed(input_value, init_project):
    result = exec_command(
        ["framefox", "create", "user"],
        input_value=f"{input_value}\n"
    )

    assert result.returncode == 0, f"Command failed with error: {result.stderr.strip()}"


def test_create_user_command_should_create_files(init_project):
    files = ["src/entity/user.py", "src/repository/user_repository.py"]

    exec_command(
        ["framefox", "create", "user"],
        input_value="\n"
    )

    for file in files:
        file_path = os.path.join(TMP_PATH, file)
        assert os.path.exists(file_path), f"File {file_path} should exist after command execution"


def test_create_user_command_when_already_done_should_fail(init_project):
    exec_command(
        ["framefox", "create", "user"],
        input_value="user\n"
    )

    result = exec_command(
        ["framefox", "create", "user"],
        input_value="user\n"
    )

    assert result.returncode != 0, "Command should fail if user already exists"
