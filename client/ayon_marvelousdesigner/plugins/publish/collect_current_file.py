"""Plugin for collecting the current working file in Marvelous Designer.

This module provides a Pyblish plugin that injects the current working file
path into the publish context for Marvelous Designer projects.
"""

from typing import ClassVar

import pyblish.api
from ayon_core.pipeline import registered_host


class CollectCurrentFile(pyblish.api.ContextPlugin):
    """Inject the current working file into context."""

    order = pyblish.api.CollectorOrder - 0.49
    label = "Current Workfile"
    hosts: ClassVar[list[str]] = ["marvelousdesigner"]

    def process(self, context: pyblish.api.Context) -> None:
        """Process the context to inject current workfile path.

        Args:
            context (pyblish.api.Context): The publish context to modify.
        """
        host = registered_host()
        path = host.get_current_workfile()
        if not path:
            self.log.error("Scene is not saved.")

        context.data["currentFile"] = path
        self.log.debug("Current workfile: %s", path)
