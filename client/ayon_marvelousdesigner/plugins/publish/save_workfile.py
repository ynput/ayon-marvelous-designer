"""Save current workfile plugin for Marvelous Designer."""
from typing import ClassVar

import pyblish.api
from ayon_core.pipeline import KnownPublishError, registered_host


class SaveCurrentWorkfile(pyblish.api.ContextPlugin):
    """Save current workfile."""

    label = "Save current workfile"
    order = pyblish.api.ExtractorOrder - 0.49
    hosts: ClassVar[list[str]] = ["marvelousdesigner"]

    def process(self, context: pyblish.api.Context) -> None:  # noqa: PLR6301
        """Process the context to save the current workfile.

        Args:
            context (pyblish.api.Context): The publishing context containing
            current file information.

        Raises:
            KnownPublishError: If the workfile has changed during publishing.
        """
        host = registered_host()
        current = host.get_current_workfile()
        if context.data["currentFile"] != current:
            msg = "Workfile has changed during publishing!"
            raise KnownPublishError(msg)

        host.save_workfile(current)
