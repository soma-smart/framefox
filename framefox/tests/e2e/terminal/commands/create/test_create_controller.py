import pytest

from framefox.tests.e2e.fixtures.commands import TMP_PATH, handle_tmp_path, init_project, exec_command


def test_create_controller_command_should_exist(init_project):
    result = exec_command(["framefox", "create", "controller", "--help"])

    assert result.returncode == 0, f"Command failed with error: {result.stderr.strip()}"

def test_create_controller_command_without_input_should_fail(init_project):
    result = exec_command(["framefox", "create", "controller"])

    assert result.returncode != 0, "Command should fail without input"

def test_create_controller_command_with_valid_input_should_succeed(init_project):
    result = exec_command(
        ["framefox", "create", "controller"],
        input_value="toto\n"
    )

    assert result.returncode == 0, f"Command failed with error: {result.stderr.strip()}"

def test_create_controller_command_when_already_executed_should_fail(init_project):
    result = exec_command(
        ["framefox", "create", "controller"],
        input_value="toto\n"
    )

    result = exec_command(
        ["framefox", "create", "controller"],
        input_value="toto\n"
    )

    assert result.returncode != 0, "Command should fail when executed again with the same name"