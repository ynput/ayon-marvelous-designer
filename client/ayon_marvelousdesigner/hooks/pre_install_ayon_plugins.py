"""Pre-launch hook for installing Ayon Plugins in Marvelous Designer.

This module provides:
InstallQtBinding: Pre-launch hook that installs PySide6 to MD's
  Python environment to enable Qt-based functionality.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import ClassVar

from ayon_applications import LaunchTypes, PreLaunchHook
from ayon_marvelousdesigner import (
    MARVELOUS_DESIGNER_HOST_DIR,
)


class InstallAyonPlugins(PreLaunchHook):
    """Install AYON plugins to Marvelous Designer's plugins."""

    app_groups: ClassVar = {"marvelousdesigner"}
    order = 12
    launch_types: ClassVar = {LaunchTypes.local}

    def execute(self) -> None:
        """Execute the pre-launch hook to install AYON plugins."""
        md_setting = self.data["project_settings"]["marvelous_designer"]
        plugins_dir = md_setting["prelaunch_settings"].get(
            "plugins_dir", "")
        plugins_dir = Path(plugins_dir)
        if not plugins_dir.exists():
            self.log.warning("Plugins directory not found: %s", plugins_dir)
            return
        plugins_json = plugins_dir / "pluginSettings.json"
        deployed_script = (
            Path(MARVELOUS_DESIGNER_HOST_DIR)
            / "deploy" / "ayon_plugins.py"
        )
        self._write_plugins_json(
            plugins_json.as_posix(),
            deployed_script.as_posix()
        )

    @staticmethod
    def _write_plugins_json(plugins_json: str, deployed_script: str) -> None:
        """Write the AYON plugin settings to a JSON file.

        Args:
            plugins_json: Path to the plugin settings JSON file.
            deployed_script: Path to the deployed plugin script to be added.
        """
        new_plugin = {
            "m_AddingPositionIndex": 1,
            "m_BaseMenuTreeByObjectName": "Plugins / Plug-in",
            "m_PlugInFileName": deployed_script,
            "m_PlugInIconFileName": "",
            "m_PlugInTitle": "ayon_plugins",
            "m_SourcePath": deployed_script,
            "m_SourceType": "script"
        }

        plugins_path = Path(plugins_json)
        # Try to read existing data
        if plugins_path.exists():
            try:
                with open(plugins_json, encoding="utf-8") as f:
                    plugins_data = json.load(f)
            except (OSError, json.JSONDecodeError):
                # If reading fails, start fresh
                plugins_data = {"plugins": [], "version": 2}
        else:
            plugins_data = {"plugins": [], "version": 2}
        # Ensure plugins list exists
        if "plugins" not in plugins_data:
            plugins_data["plugins"] = []

        # Check if plugin already exists (avoid duplicates)
        existing_titles = {
            existing_plugins.get("m_PlugInTitle")
            for existing_plugins in plugins_data["plugins"]
        }
        if "ayon_plugins" not in existing_titles:
            plugins_data["plugins"].append(new_plugin)

        # Write the updated data
        with open(plugins_json, "w", encoding="utf-8") as f:
            json.dump(plugins_data, f, indent=4)
