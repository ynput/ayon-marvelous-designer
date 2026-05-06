"""Pre-launch hook for installing Qt bindings in Marvelous Designer.

This module provides:
InstallQtBinding: Pre-launch hook that installs PySide6 to MD's
  Python environment to enable Qt-based functionality.
"""
from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import ClassVar, Union

from ayon_applications import LaunchTypes, PreLaunchHook

# PySide6 packages to download from PyPI.
# Must stay in dependency order: shiboken6 first, then PySide6 core.
_PYSIDE6_VERSION = "6.10.1"
_PYSIDE6_PACKAGES = [
    "shiboken6",
    "PySide6",
    "PySide6-Essentials",
    "PySide6-Addons",
]


class InstallQtBinding(PreLaunchHook):
    """Install Qt binding to unreal's python packages."""

    app_groups: ClassVar = {"marvelousdesigner"}
    order = 11
    launch_types: ClassVar = {LaunchTypes.local}

    def execute(self) -> None:
        """Execute the pre-launch hook to install PySide6."""
        md_setting = self.data["project_settings"]["marvelous_designer"]
        qt_binding_dir = md_setting["prelaunch_settings"].get(
            "qt_binding_dir", "")
        qt_binding_dir = Path(qt_binding_dir)
        if not qt_binding_dir.exists():
            self.log.warning(
                "Qt binding directory '%s' does not exist.", qt_binding_dir
            )
            return

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
            f"PySide6=={_PYSIDE6_VERSION}",
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
        """Download PySide6 wheels from PyPI to a temp dir and extract them.

        Args:
            qt_binding_dir (Path): The directory to extract wheel contents
                into.

        Returns:
            bool: True if all wheels were downloaded and extracted
                successfully, False otherwise.

        """
        tmp_dir = Path(tempfile.mkdtemp(prefix="ayon_pyside6_"))
        try:
            for package in _PYSIDE6_PACKAGES:
                if self._is_package_extracted(
                    qt_binding_dir, package, _PYSIDE6_VERSION
                ):
                    self.log.info(
                        "%s==%s already extracted, skipping.",
                        package,
                        _PYSIDE6_VERSION,
                    )
                    continue

                self.log.info("Resolving compatible wheel for %s ...", package)
                wheel_path, wheel_filename = self._download_wheel_from_pypi(
                    package, _PYSIDE6_VERSION, tmp_dir
                )
                with zipfile.ZipFile(wheel_path, "r") as zip_ref:
                    zip_ref.extractall(qt_binding_dir)
                self.log.info("Extracted %s", wheel_filename)
        except Exception as error:
            self.log.warning(
                'Failed to download/extract wheels: "%s".', error,
                exc_info=True)
            return False
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        return True

    @staticmethod
    def _is_package_extracted(
            qt_binding_dir: Path, package: str, version: str) -> bool:
        """Return whether a package/version appears to already be extracted.

        Args:
            qt_binding_dir(Path): Directory where the package is extracted.
            package (str): PyPI package name.
            version (str): Exact version string.

        Returns:
            bool: True if the package appears to be already extracted,
                False otherwise.
        """
        normalized = package.lower().replace("-", "_")
        dist_info_name = f"{normalized}-{version}.dist-info"

        for path in qt_binding_dir.glob("*.dist-info"):
            if path.name.lower() == dist_info_name:
                return True

        return False

    @staticmethod
    def _download_wheel_from_pypi(
            package: str, version: str,
            dest_dir: Path) -> tuple[Path, str]:
        """Download a compatible wheel from PyPI using the JSON API.

        Args:
            package (str): PyPI package name.
            version: Exact version string.
            dest_dir: Directory to save the downloaded wheel.

        Returns:
            tuple[Path, str]: Downloaded wheel path and wheel filename.

        """
        api_url = f"https://pypi.org/pypi/{package}/{version}/json"
        with urllib.request.urlopen(api_url, timeout=60) as resp:
            data = json.loads(resp.read())
        wheel_url_info = InstallQtBinding._select_compatible_wheel_url(
            package, version, data.get("urls", [])
        )
        wheel_filename = wheel_url_info["filename"]
        dest = dest_dir / wheel_filename
        urllib.request.urlretrieve(wheel_url_info["url"], dest)  # noqa: S310
        return dest, wheel_filename

    @staticmethod
    def _select_compatible_wheel_url(
            package: str, version: str, urls: list[dict]) -> dict:
        """Pick the best matching wheel entry for the current OS/arch.

        Args:
            package: PyPI package name.
            version: Exact version string.
            urls: List of URL info dicts from PyPI JSON API.

        Returns:
            dict: The URL info dict for the best matching wheel.

        Raises:
            FileNotFoundError: If no compatible wheel is found.
        """
        normalized_package = package.lower().replace("-", "_")
        prefix = f"{normalized_package}-{version}-cp39-abi3-"

        candidates = [
            url_info
            for url_info in urls
            if url_info.get("packagetype") == "bdist_wheel"
            and url_info.get("filename", "").lower().startswith(prefix)
        ]

        if not candidates:
            msg = (
                f"No cp39-abi3 wheel candidates found for "
                f"{package}=={version} on PyPI"
            )
            raise FileNotFoundError(msg)

        platform_key = sys.platform
        machine = platform.machine().lower()

        preferred_tags = InstallQtBinding._preferred_tags(
            platform_key, machine
        )

        def _score(filename: str) -> int:
            lowered = filename.lower()
            score = 0
            for tag in preferred_tags:
                if tag in lowered:
                    score += 1
            return score

        best = max(
            candidates,
            key=lambda url_info: _score(url_info["filename"]),
        )
        if _score(best["filename"]) == 0:
            available = ", ".join(
                url_info["filename"] for url_info in candidates
            )
            msg = (
                f"No compatible wheel found for {package}=={version} on "
                f"platform={platform_key}, arch={machine}. "
                f"Available: {available}"
            )
            raise FileNotFoundError(msg)

        return best

    @staticmethod
    def _preferred_tags(platform_key: str, machine: str) -> list[str]:
        """Return tag preferences for selecting a platform-specific wheel.

        Raises:
            RuntimeError: If the platform is unsupported.

        """
        if platform_key.startswith("win"):
            return ["win_amd64"]
        if platform_key.startswith("linux"):
            if machine in {"aarch64", "arm64"}:
                return ["manylinux", "aarch64", "arm64"]
            return ["manylinux", "x86_64", "amd64"]
        if platform_key == "darwin":
            if machine in {"arm64", "aarch64"}:
                return ["macosx", "universal2", "arm64"]
            return ["macosx", "universal2", "x86_64"]

        msg = f"Unsupported platform for wheel selection: {platform_key}"
        raise RuntimeError(msg)
