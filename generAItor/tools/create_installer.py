import argparse
import os
import os.path
import re
import shutil
import subprocess
import sys
import zipfile
from enum import Enum
from typing import List

SEPARATOR_LINE = "-" * 80


class SupportedTarget(str, Enum):
    """
    All the supported OS Targets
    """

    LINUX = "linux"
    WINDOWS = "windows"
    MACOS = "macos"


def get_version() -> str:
    """
    Gets the Code-Generator version.
    :return: The CG version.
    """
    with open("code_generator/__init__.py", "r") as file:
        file_content = file.read()

    for line in file_content.splitlines():
        if line.startswith("__version__"):
            return line.split('"' if '"' in line else "'")[1]
    raise ValueError("Unable to find version string.")


def run_command(params: List[str]) -> None:
    """
    Runs a given command and gets the return code.

    :param params: A list with the params of the command to be executed.
    :return: None.
    """
    result = subprocess.Popen(params)
    result.communicate()[0]
    if result.returncode != 0:
        raise RuntimeError(f"Error executing command: '{' '.join(params)}'")


def remove_dir(directory: str) -> None:
    """
    Removes a directory if it exists.
    :param directory: The dir to be removed.
    :return: None.
    """
    if os.path.exists(directory):
        shutil.rmtree(directory)


def clean_build_dirs() -> None:
    """
    Cleans all the generated intermediate dirs.
    :return: None.
    """
    remove_dir("build")
    remove_dir("dist")
    remove_dir("code_generator.egg-info")


def install_pyinstaller(target: str) -> None:
    """
    Installs PyInstaller.
    :param target: The target OS machine.
    :return: None.
    """
    pip_command = "pip" if target == SupportedTarget.WINDOWS else "pip3"
    run_command([pip_command, "install", "pyinstaller"])


def install_dependencies(target: SupportedTarget) -> None:
    """
    Install all the prod dependencies.
    :param target: The target OS machine.
    :return: None.
    """
    pip_command = "pip" if target == SupportedTarget.WINDOWS else "pip3"
    pip_command_params = [pip_command, "install", "-r", "requirements/prod.txt"]

    if target == SupportedTarget.MACOS:
        pip_command_params.append("--user")

    run_command(pip_command_params)


def create_installer(target: SupportedTarget) -> None:
    """
    Creates the installer running the `pyinstaller` command.
    :param target: The target OS machine.
    :return: None.
    """
    separator = ";" if target == SupportedTarget.WINDOWS else ":"
    params = [
        "pyinstaller",
        "--paths=code_generator",
        "--name=code_generator_tool",
        f"--add-data=diagrams/*.png{separator}diagrams",
        f"--add-data=code_generator/config_reader/config.schema{separator}code_generator/config_reader",
        f"--add-data=*.md{separator}.",
        f"--add-data=.env.sample{separator}.",
        "code_generator/__main__.py",
    ]
    if target == SupportedTarget.WINDOWS:
        params.append(f"--add-data=venv/Scripts/pygount.exe{separator}.")
    run_command(params)


def create_zip_file(dir_to_compress: str, zip_name: str) -> None:
    """
    Generates a zip file.
    :param dir_to_compress: The directory to be zipped.
    :param zip_name: The name of the zip file.
    :return: None.
    """
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as archive_file:
        for dirpath, dirnames, filenames in os.walk(dir_to_compress):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                archive_file_path = os.path.relpath(file_path, dir_to_compress)
                archive_file.write(file_path, archive_file_path)


def validate_target_arg(value: str) -> SupportedTarget:
    """
    Validates if the given target is valid or not.
    :param value: The value to validate.
    :return: A valid target.
    :raises: A ArgumentTypeError exception if the target is invalid.
    """
    if value in SupportedTarget.__members__.values():
        return SupportedTarget(value).value
    raise argparse.ArgumentTypeError(f"Must be one of {[item.value for item in SupportedTarget]}.")


def main() -> None:
    """
    The main function.
    Arguments to be used [target:str] [upload:bool] [publish:bool].
    [target] can be one of SupportedTarget values.
    [upload] is a boolean.
    [publish] is a boolean.
    :return: None.
    """
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--target",
            type=validate_target_arg,
            required=True,
            help=f"The OS target. Can be one of {[item.value for item in SupportedTarget]}.",
        )
        args = parser.parse_args()

        version = get_version()
        zip_name = f"code_generator_{args.target}_{version}.zip"

        clean_build_dirs()
        install_pyinstaller(target=args.target)
        install_dependencies(target=args.target)

        print(SEPARATOR_LINE)
        print(f"Creating installer for Code-Generator version: {version}")
        create_installer(target=args.target)
        print("  Done.")

        print(SEPARATOR_LINE)
        print(f"Creating zip file '{zip_name}'...")
        create_zip_file(dir_to_compress="dist", zip_name=zip_name)
        file_size = os.path.getsize(zip_name) / (1024 * 1024)
        print("  Done.")

    except Exception as ex:
        print(f"ERROR: {ex}")
        sys.exit(1)


if __name__ == "__main__":
    main()
