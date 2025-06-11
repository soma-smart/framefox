import subprocess
import pytest

from framefox.tests.e2e.fixtures.commands import TMP_PATH, handle_tmp_path, init_project, exec_command


def test_create_entity_command_should_exist(init_project):
    result = exec_command(["framefox", "create", "entity", "--help"])

    assert result.returncode == 0, f"Command failed with error: {result.stderr.strip()}"

def test_create_entity_command_without_input_should_fail(init_project):
    result = exec_command(["framefox", "create", "entity"])

    assert result.returncode != 0, "Command should fail without input"

@pytest.mark.parametrize("input_value", ["", "name\n\n\n\n", "age\nint\n\n", "price\nfloat\n\n", "available\nbool\n\n", "classes\nlist\n\n", "map\ndict\n\n", "map\ntuple\n\n", "when\ndate\n\n"])
def test_create_entity_command_with_valid_input_should_succeed(input_value, init_project):
    result = exec_command(
        ["framefox", "create", "entity"],
        input_value=f"toto\n{input_value}\n"
    )

    assert result.returncode == 0, f"Command failed with error: {result.stderr.strip()}"