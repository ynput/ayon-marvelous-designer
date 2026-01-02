"""Pre-launch hook for installing Qt bindings in Marvelous Designer.

This module provides:
- InstallQtBinding: Pre-launch hook that installs PySide6 to MD's
  Python environment to enable Qt-based functionality.
"""
from __future__ import annotations

import platform
import subprocess
from pathlib import Path
from typing import ClassVar, Union

from ayon_applications import LaunchTypes, PreLaunchHook


class InstallQtBinding(PreLaunchHook):
    """Install Qt binding to unreal's python packages."""

    app_groups: ClassVar = {"marvelousdesigner"}
    order = 11
    launch_types: ClassVar = {LaunchTypes.local}

    def execute(self) -> None:
        """Execute the pre-launch hook to install PySide6."""
        current_platform = platform.system().lower()
        python_executable = (
            "python"
            if current_platform != "windows"
            else "python.exe"
        )
        md_setting = self.data["project_settings"]["marvelous_designer"]
        qt_binding_dir = md_setting["prelaunch_settings"].get(
            "qt_binding_dir", "")
        qt_binding_dir = Path(qt_binding_dir)
        if not qt_binding_dir.exists():
            self.log.warning(
                "Qt binding directory '%s' does not exist.", qt_binding_dir
            )
            return

        return_code = self.install_pyside(python_executable, qt_binding_dir)
        if return_code:
            self.log.info("PySide6 installed successfully.")
            self.launch_context.env["QtDir"] = qt_binding_dir.as_posix()

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
            "PySide6",
            "--target",
            qt_binding_dir.as_posix()
        ]

        return self.pip_install(args)

    def pip_install(self, args: list) -> Union[bool, None]:
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
                args, stdout=subprocess.PIPE, universal_newlines=True
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
