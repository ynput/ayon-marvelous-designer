import pyblish.api

from ayon_core.pipeline import (
    registered_host,
    KnownPublishError
)


class SaveCurrentWorkfile(pyblish.api.ContextPlugin):
    """Save current workfile"""

    label = "Save current workfile"
    order = pyblish.api.ExtractorOrder - 0.49
    hosts = ["marvelousdesigner"]

    def process(self, context):

        host = registered_host()
        current = host.get_current_workfile()
        if context.data["currentFile"] != current:
            raise KnownPublishError("Workfile has changed during publishing!")

        host.save_workfile(current)
