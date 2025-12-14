# -*- coding: utf-8 -*-
"""Collect current work file."""
import os
from pathlib import Path
import pyblish.api


class CollectWorkfile(pyblish.api.InstancePlugin):
    """Inject the current working file into context"""

    order = pyblish.api.CollectorOrder - 0.01
    label = "Collect Workfile"
    hosts = ['marvelousdesigner']
    families = ["workfile"]

    def process(self, instance):
        """Inject the current working file."""
        context = instance.context
        current_file = context.data.get("currentFile")
        filepath = Path(current_file)
        ayon_temp_dir = os.getenv("AYON_TEMP_DIR", "")
        if ayon_temp_dir and filepath.parent == ayon_temp_dir:
            self.log.warning("Deactivating workfile instance because no "
                             "current filepath is found. Please save your "
                             "workfile.")
            instance.data["publish"] = False
            return

        ext = filepath.suffix
        instance.data.update(
            {
                "setMembers": [filepath.as_posix()],
                "frameStart": context.data.get("frameStart", 1),
                "frameEnd": context.data.get("frameEnd", 1),
                "handleStart": context.data.get("handleStart", 1),
                "handledEnd": context.data.get("handleEnd", 1),
                "representations": [
                    {
                        "name": ext.lstrip("."),
                        "ext": ext.lstrip("."),
                        "files": filepath.name,
                        "stagingDir": filepath.parent,
                    }
                ],
            }
        )
