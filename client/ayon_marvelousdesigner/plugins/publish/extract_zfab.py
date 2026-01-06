"""Extract zfab Format Plugin for Marvelous Designer in Ayon."""
import os
from typing import ClassVar

import fabric_api
import pyblish.api
from ayon_core.pipeline import publish


class ExtractZFab(publish.Extractor):
    """Extract Geometry in Alembic Format."""

    order = pyblish.api.ExtractorOrder - 0.05
    label = "Extract Zfab"
    hosts: ClassVar = ["marvelousdesigner"]
    families: ClassVar = ["zfab"]

    def process(self, instance: pyblish.api.Instance) -> None:
        """Process the instance to extract zfab data."""
        stagingdir = self.staging_dir(instance)
        filename = f"{instance.name}.zfab"
        filepath = os.path.join(stagingdir, filename)
        target_fabric_index = instance.data["fabricIndex"]

        fabric_api.ExportZFab(filepath, target_fabric_index)
        if "representations" not in instance.data:
            instance.data["representations"] = []

        representation = {
            "name": "zfab",
            "ext": "zfab",
            "files": filename,
            "stagingDir": stagingdir,
        }

        instance.data["representations"].append(representation)
        self.log.info(
            f"Extracted instance '{instance.name}' to: {filepath}"  # noqa: G004
        )
