import subprocess
import shutil
import pytest
import os


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


def test_create_entity_command_should_exist():
    result = subprocess.run(
        ["framefox", "create", "entity", "--help"],
        cwd=TMP_PATH,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Command failed with error: {result.stderr.strip()}"

def test_create_entity_command_without_input_should_fail():
    result = subprocess.run(
        ["framefox", "create", "entity"],
        cwd=TMP_PATH,
        capture_output=True,
        text=True
    )

    assert result.returncode != 0, "Command should fail without input"

@pytest.mark.parametrize("input_value", ["", "name\n\n\n\n", "age\nint\n\n", "price\nfloat\n\n", "available\nbool\n\n", "classes\nlist\n\n", "map\ndict\n\n", "map\ntuple\n\n", "when\ndate\n\n"])
def test_create_entity_command_with_valid_input_should_succeed(input_value):
    result = subprocess.run(
        ["framefox", "create", "entity"],
        cwd=TMP_PATH,
        input=f"toto\n{input_value}\n",
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Command failed with error: {result.stderr.strip()}"