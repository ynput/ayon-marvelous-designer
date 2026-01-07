"""Marvelous Designer integration addon for AYON.

This module provides the MarvelousDesignerAddon class which integrates
Marvelous Designer host application with the AYON pipeline.
"""
import os

from ayon_core.addon import AYONAddon, IHostAddon

from .version import __version__

MARVELOUS_DESIGNER_HOST_DIR = os.path.dirname(os.path.abspath(__file__))


class MarvelousDesignerAddon(AYONAddon, IHostAddon):
    """Addon class for Marvelous Designer integration with AYON.

    This addon provides host integration capabilities for Marvelous Designer,
    including launch hooks, environment setup, and workfile extensions.
    """
    name = "marvelousdesigner"
    version = __version__
    host_name = "marvelousdesigner"

    def add_implementation_envs(self, env: dict, _app: object) -> None:  # noqa: PLR6301
        """Add environment variables specific to Marvelous Designer host."""
        env.pop("QT_AUTO_SCREEN_SCALE_FACTOR", None)

    def get_launch_hook_paths(self, app: object) -> list[str]:
        """Get paths to launch hook directories for Marvelous Designer.

        Args:
            app: Application object containing host information.

        Returns:
            List of paths to hook directories, or empty list if not applicable.
        """
        if app.host_name != self.host_name:
            return []
        return [
            os.path.join(MARVELOUS_DESIGNER_HOST_DIR, "hooks")
        ]

    def get_workfile_extensions(self) -> list[str]:  # noqa: PLR6301
        """Get supported workfile extensions for Marvelous Designer.

        Returns:
            List of supported workfile extensions.
        """
        return [".zprj"]
