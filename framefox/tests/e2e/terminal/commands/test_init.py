import subprocess
import shutil
import pytest
import os

from framefox.terminal.commands.init_command import PROJECT_DIRECTORIES, PROJECT_FILES


TMP_PATH = "test_dir"


@pytest.fixture(autouse=True)
def handle_tmp_path():
    if os.path.exists(TMP_PATH):
        shutil.rmtree(TMP_PATH)
    os.mkdir(TMP_PATH)

    yield
    if os.path.exists(TMP_PATH):
        shutil.rmtree(TMP_PATH)


def test_init_command_should_exist(handle_tmp_path):
    result = subprocess.run(
        ["framefox", "init"],
        cwd=TMP_PATH,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0

def test_init_command_should_create_folders(handle_tmp_path):
    result = subprocess.run(
        ["framefox", "init"],
        cwd=TMP_PATH,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0

    for directory in PROJECT_DIRECTORIES:
        assert os.path.exists(os.path.join(TMP_PATH, directory)), f"Directory {directory} was not created"

def test_init_command_should_create_files(handle_tmp_path):
    result = subprocess.run(
        ["framefox", "init"],
        cwd=TMP_PATH,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    
    for file in PROJECT_FILES:
        file_path = os.path.join(TMP_PATH, file)
        assert os.path.exists(file_path), f"File {file} was not created"


def test_init_command_when_already_done_should_fail(handle_tmp_path):
    subprocess.run(
        ["framefox", "init"],
        cwd=TMP_PATH,
        capture_output=True,
        text=True
    )

    result = subprocess.run(
        ["framefox", "init"],
        cwd=TMP_PATH,
        capture_output=True,
        text=True
    )

    assert result.returncode == 1