import os
from typing import ClassVar

import fabric_api
import pyblish.api
from ayon_core.pipeline import publish


class ExtractPointCache(publish.Extractor):
    """Extract Geometry in Alembic Format."""

    order = pyblish.api.ExtractorOrder - 0.05
    label = "Extract Zfab"
    hosts: ClassVar = ["marvelousdesigner"]
    families: ClassVar = ["zfab"]

    def process(self, instance: pyblish.api.Instance) -> None:
        stagingdir = self.staging_dir(instance)
        filename = f"{instance.name}.zfab"
        filepath = os.path.join(stagingdir, filename)
        target_fabric_index = instance.data["fabricIndex"]

        fabric_api.ExportZFab(filepath, target_fabric_index)

        representation = {
            "name": "zfab",
            "ext": "zfab",
            "files": filename,
            "stagingDir": stagingdir,
        }

        instance.data["representations"].append(representation)
        self.log.info(
            "Extracted instance '%s' to: %s" % (instance.name, filepath)
        )
