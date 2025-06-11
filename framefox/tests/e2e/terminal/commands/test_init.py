import subprocess
import shutil
import pytest
import os

from framefox.terminal.commands.init_command import PROJECT_DIRECTORIES, PROJECT_FILES
from framefox.tests.e2e.fixtures.commands import TMP_PATH, handle_tmp_path, exec_command


def test_init_command_should_exist(handle_tmp_path):
    result = exec_command(
        ["framefox", "init", "--help"],
    )

    assert result.returncode == 0

def test_init_command_should_create_folders(handle_tmp_path):
    result = exec_command(
        ["framefox", "init"],
    )

    assert result.returncode == 0

    for directory in PROJECT_DIRECTORIES:
        assert os.path.exists(os.path.join(TMP_PATH, directory)), f"Directory {directory} was not created"

def test_init_command_should_create_files(handle_tmp_path):
    result = exec_command(
        ["framefox", "init"],
    )

    assert result.returncode == 0

    for file in PROJECT_FILES:
        file_path = os.path.join(TMP_PATH, file)
        assert os.path.exists(file_path), f"File {file_path} was not created"


def test_init_command_when_already_done_should_fail(handle_tmp_path):
    exec_command(
        ["framefox", "init"],
    )
    result = exec_command(
        ["framefox", "init"],
    )

    assert result.returncode == 1