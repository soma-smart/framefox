from framefox.tests.e2e.fixtures.commands import exec_command  # noqa: F401
from framefox.tests.e2e.fixtures.commands import (
    handle_tmp_path,
    init_project,
)


def testest_create_crud_command_should_exist(init_project):  # noqa: F811
    result = exec_command(["framefox", "create", "crud", "--help"])

    assert result.returncode == 0, f"Command failed with error: {result.stderr.strip()}"


def test_create_crud_command_without_input_should_fail(init_project):  # noqa: F811
    result = exec_command(["framefox", "create", "crud"])

    assert result.returncode != 0, "Command should fail without input"


def test_create_crud_command_without_entity_but_valid_input_should_fail(
    init_project,
):  # noqa: F811
    result = exec_command(["framefox", "create", "crud"], input_value="toto\n\n")

    assert result.returncode != 0, "Command should fail without entity"


def test_create_crud_command_with_valid_input_should_succeed(
    init_project,
):  # noqa: F811
    exec_command(["framefox", "create", "entity"], input_value="toto\n")
    result = exec_command(["framefox", "create", "crud"], input_value="toto\n\n")

    assert result.returncode == 0, f"Command failed with error: {result.stderr.strip()}"
