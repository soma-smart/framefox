import os

from framefox.tests.e2e.fixtures.commands import TMP_PATH  # noqa: F401
from framefox.tests.e2e.fixtures.commands import (
    exec_command,
    handle_tmp_path,
    init_project,
)


def test_create_user_command_should_exist(init_project):  # noqa: F811
    result = exec_command(["framefox", "create", "user", "--help"])

    assert result.returncode == 0, f"Command failed with error: {result.stderr.strip()}"


def test_create_user_command_without_input_should_fail(init_project):  # noqa: F811
    result = exec_command(["framefox", "create", "user"])

    assert result.returncode != 0, "Command should fail without input"


def test_create_user_with_invalid_name_should_fail(init_project):  # noqa: F811
    os.makedirs(os.path.join(TMP_PATH, "src", "entity"), exist_ok=True)
    os.makedirs(os.path.join(TMP_PATH, "src", "repository"), exist_ok=True)

    result = exec_command(["framefox", "create", "user"], input_value="InvalidUserName\n")

    assert result.returncode != 0, "Command should fail with invalid entity name format"
