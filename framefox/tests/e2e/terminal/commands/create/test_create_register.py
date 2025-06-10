import pytest

from framefox.tests.e2e.fixtures.commands import TMP_PATH, handle_tmp_path, init_project, exec_command


def test_create_register_command_should_exist(init_project):
    result = exec_command(["framefox", "create", "register", "--help"])

    assert result.returncode == 0, f"Command failed with error: {result.stderr.strip()}"

def test_create_register_command_without_input_should_fail(init_project):
    result = exec_command(["framefox", "create", "register"])

    assert result.returncode != 0, "Command should fail without input"

def test_create_register_command_with_user_and_correct_inputs_should_succeed(init_project):
    exec_command(["framefox", "create", "user"], input_value="\n")

    result = exec_command(
        ["framefox", "create", "register"],
        input_value="user\n"
    )

    assert result.returncode == 0, f"Command failed with error: {result.stderr.strip()}"

def test_create_register_command_without_user_but_correct_inputs_should_fail(init_project):
    result = exec_command(
        ["framefox", "create", "register"],
        input_value="user\n"
    )

    assert result.returncode != 0, f"Command succeeded unexpectedly"

def test_create_register_command_when_already_done_should_fail(init_project):
    exec_command(
        ["framefox", "create", "register"],
        input_value="\n"
    )

    result = exec_command(
        ["framefox", "create", "register"],
        input_value="\n"
    )

    assert result.returncode != 0, "Command should fail when register files already exist"