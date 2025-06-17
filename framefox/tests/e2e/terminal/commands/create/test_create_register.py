import os

import pytest

from framefox.tests.e2e.fixtures.commands import (
    TMP_PATH,
    exec_command,
    handle_tmp_path,
    init_project,
)


def test_create_register_command_should_exist(init_project):
    result = exec_command(["framefox", "create", "register", "--help"])

    assert result.returncode == 0, f"Command failed with error: {result.stderr.strip()}"


def test_create_register_command_without_input_should_fail(init_project):
    result = exec_command(["framefox", "create", "register"])

    assert result.returncode != 0, "Command should fail without input"


def test_create_register_command_without_user_but_correct_inputs_should_fail(init_project):
    os.makedirs(os.path.join(TMP_PATH, "src", "entity"), exist_ok=True)
    os.makedirs(os.path.join(TMP_PATH, "src", "repository"), exist_ok=True)

    result = exec_command(["framefox", "create", "register"], input_value="user\n")

    assert result.returncode != 0, f"Command should fail without existing user entity"


def test_create_register_with_nonexistent_entity_should_fail(init_project):
    os.makedirs(os.path.join(TMP_PATH, "src", "entity"), exist_ok=True)
    os.makedirs(os.path.join(TMP_PATH, "src", "repository"), exist_ok=True)

    result = exec_command(["framefox", "create", "register"], input_value="nonexistent_user\n")

    assert result.returncode != 0, "Command should fail with nonexistent user entity"
