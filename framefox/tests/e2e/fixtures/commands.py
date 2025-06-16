import pytest
import subprocess
import shutil
import os


TMP_PATH = "test_dir"

@pytest.fixture()
def handle_tmp_path():
    if os.path.exists(TMP_PATH):
        shutil.rmtree(TMP_PATH)

    os.mkdir(TMP_PATH)
    yield TMP_PATH
    if os.path.exists(TMP_PATH):
        shutil.rmtree(TMP_PATH)


@pytest.fixture()
def init_project(handle_tmp_path):
    result = subprocess.run(
        ["framefox", "init"],
        cwd=TMP_PATH,
        capture_output=True,
        text=True
    )

def exec_command(command, input_value=None):
    result = subprocess.run(
        command,
        cwd=TMP_PATH,
        input=input_value,
        capture_output=True,
        text=True
    )
    return result
