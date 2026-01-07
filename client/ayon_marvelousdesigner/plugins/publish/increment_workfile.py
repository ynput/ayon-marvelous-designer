"""Pyblish plugin for incrementing workfile version after successful publish.

This module contains a plugin that automatically increments the current
workfile version number after a successful publish operation in MD.
"""
import os
from typing import ClassVar

import pyblish.api
from ayon_core.lib import version_up
from ayon_core.pipeline import KnownPublishError, registered_host


class IncrementWorkfileVersion(pyblish.api.ContextPlugin):
    """Increment current workfile version."""

    order = pyblish.api.IntegratorOrder + 1
    label = "Increment Workfile Version"
    optional = True
    hosts: ClassVar[list[str]] = ["marvelousdesigner"]

    def process(self, context: pyblish.api.Context) -> None:
        """Process the context to increment the workfile version.

        Args:
            context (pyblish.api.Context): The publishing context.

        Raises:
            KnownPublishError: If the publishing was not successful.
        """
        if not all(result["success"] for result in context.data["results"]):
            msg = "Publishing not successful so version is not increased."
            raise KnownPublishError(msg)

        host = registered_host()
        current_filepath = context.data["currentFile"]
        try:
            from ayon_core.host.interfaces import SaveWorkfileOptionalData
            from ayon_core.pipeline.workfile import save_next_version

            current_filename = os.path.basename(current_filepath)
            save_next_version(
                description=(
                    f"Incremented by publishing from {current_filename}"
                ),
                # Optimize the save by reducing needed queries for context
                prepared_data=SaveWorkfileOptionalData(
                    project_entity=context.data["projectEntity"],
                    project_settings=context.data["project_settings"],
                    anatomy=context.data["anatomy"],
                )
            )
            new_filepath = host.get_current_workfile()

        except ImportError:
            # Backwards compatibility before ayon-core 1.5.0
            self.log.debug(
                "Using legacy `version_up`. Update AYON core addon to "
                "use newer `save_next_version` function."
            )
            new_filepath = version_up(current_filepath)
            host.save_workfile(new_filepath)

        self.log.info("Incrementing current workfile to: %s", new_filepath)
