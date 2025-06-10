import pytest
import os
import shutil
import subprocess


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


def test_create_user_command_should_exist():
    result = subprocess.run(
        ["framefox", "create", "user", "--help"],
        cwd=TMP_PATH,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Command failed with error: {result.stderr.strip()}"


def test_create_user_command_without_input_should_fail():
    result = subprocess.run(
        ["framefox", "create", "user"],
        cwd=TMP_PATH,
        capture_output=True,
        text=True
    )

    assert result.returncode != 0, "Command should fail without input"


@pytest.mark.parametrize("input_value", ["\n", "user\n"])
def test_create_user_command_with_valid_input_should_succeed(input_value):
    result = subprocess.run(
        ["framefox", "create", "user"],
        cwd=TMP_PATH,
        input=input_value,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Command failed with error: {result.stderr.strip()}"


def test_create_user_command_should_create_files():
    files = ["src/entity/user.py", "src/repository/user_repository.py"]

    subprocess.run(
        ["framefox", "create", "user"],
        cwd=TMP_PATH,
        input="\n",
        capture_output=True,
        text=True
    )

    for file in files:
        file_path = os.path.join(TMP_PATH, file)
        assert os.path.exists(file_path), f"File {file_path} should exist after command execution"


def test_create_user_command_when_already_done_should_fail():
    result = subprocess.run(
        ["framefox", "create", "user"],
        cwd=TMP_PATH,
        input="user\n",
        capture_output=True,
        text=True
    )

    result = subprocess.run(
        ["framefox", "create", "user"],
        cwd=TMP_PATH,
        input="user\n",
        capture_output=True,
        text=True
    )

    assert result.returncode != 0, "Command should fail if user already exists"
