"""Pre-launch hook for installing Qt bindings in Marvelous Designer.

This module provides:
- InstallQtBinding: Pre-launch hook that installs PySide6 to MD's
  Python environment to enable Qt-based functionality.
"""
from __future__ import annotations

import platform
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import ClassVar, Union

from ayon_applications import LaunchTypes, PreLaunchHook
from ayon_marvelousdesigner import MARVELOUS_DESIGNER_HOST_DIR


class InstallQtBinding(PreLaunchHook):
    """Install Qt binding to unreal's python packages."""

    app_groups: ClassVar = {"marvelousdesigner"}
    order = 11
    launch_types: ClassVar = {LaunchTypes.local}

    def execute(self) -> None:
        """Execute the pre-launch hook to install PySide6."""
        current_platform = platform.system().lower()
        md_setting = self.data["project_settings"]["marvelous_designer"]
        qt_binding_dir = md_setting["prelaunch_settings"].get(
            "qt_binding_dir", "")
        qt_binding_dir = Path(qt_binding_dir)
        if not qt_binding_dir.exists():
            self.log.warning(
                "Qt binding directory '%s' does not exist.", qt_binding_dir
            )
            return
        if current_platform != "windows":
            return_code = self.install_pyside(sys.executable, qt_binding_dir)
        else:
            return_code = self.extract_wheels(qt_binding_dir)
        if return_code:
            self.log.info("PySide6 installed successfully.")
            self.launch_context.env["QtDir"] = qt_binding_dir.as_posix()
            plugin_dir = qt_binding_dir / "PySide6" / "plugins"
            self.launch_context.env["QT_PLUGIN_PATH"] = (
                plugin_dir.as_posix()
            )

    def install_pyside(
            self, python_executable: str,
            qt_binding_dir: Path) -> Union[int, None]:
        """Install PySide6 python module to marvelous designer's python.

        Installation requires administration rights that's why it is required
        to use "pywin32" module which can execute command's and ask for
        administration rights.

        Note:
            This is asking for administrative right always, no matter if
            it is actually needed or not. Unfortunately getting
            correct permissions for directory on Windows isn't that trivial.
            You can either use `win32security` module or run `icacls` command
            in subprocess and parse its output.

        Returns:
            Return code from the pip install process, or None
            if installation fails.

        """
        args = [
            python_executable,
            "-m",
            "pip",
            "install",
            # we need to specify exact version of PySide6 to make sure
            # it is binary compatible with Marvelous Designer's python version
            "PySide6==6.10.1",
            "--target",
            qt_binding_dir.as_posix(),
            "--ignore-installed",
        ]

        return self.pip_install(args)

    def pip_install(self, args: list) -> Union[int, None]:
        """Execute pip install command in subprocess.

        Args:
            args (list): List of command line arguments for pip install.

        Returns:
            bool or None: True if pip install was successful (return code 0),
            None if an exception occurred during execution.

        """
        try:
            # Parameters
            # - use "-m pip" as module pip to install PySide2/6 and argument
            #   "--ignore-installed" is to force install module to unreal
            #   site-packages and make sure it is binary compatible

            process = subprocess.Popen(
                args, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, universal_newlines=True
            )
            process.communicate()

        except PermissionError:
            self.log.warning(
                'Permission denied with command: "%s".', " ".join(args),
                exc_info=True)
        except OSError as error:
            self.log.warning(
                'OS error has occurred: "%s".', error, exc_info=True)
        except subprocess.SubprocessError:
            pass
        else:
            return process.returncode == 0

        return None

    def extract_wheels(self, qt_binding_dir: Path) -> bool:
        """Extract wheel files in the specified directory.

        Args:
            qt_binding_dir (Path): The directory containing the wheel files
                to extract.

        Returns:
            bool: True if extraction was successful, False otherwise.

        """
        wheel_dir = Path(MARVELOUS_DESIGNER_HOST_DIR) / "wheels"
        try:
            for wheel_file in wheel_dir.glob("*.whl"):
                with zipfile.ZipFile(wheel_file, "r") as zip_ref:
                    zip_ref.extractall(qt_binding_dir)

        except Exception as error:
            self.log.warning(
                'Failed to extract wheel files: "%s".', error, exc_info=True)
            return False
        return True
