"""Extract zfab Format Plugin for Marvelous Designer in Ayon."""
from __future__ import annotations

import os
from pathlib import Path
from typing import ClassVar

import fabric_api
import pyblish.api
from ayon_core.pipeline import publish
from ayon_core.pipeline.publish import (
    add_trait_representations,
)
from ayon_core.pipeline.traits import (
    FileLocation,
    Persistent,
    Representation,
    Static,
)


class ExtractZFab(publish.Extractor):
    """Extract zfab Format.

    Contains the property values (texture + physical properties)
    of the set Fabric.
    """
    order = pyblish.api.ExtractorOrder - 0.05
    label = "Extract Zfab"
    hosts: ClassVar[list[str]] = ["marvelousdesigner"]
    families: ClassVar[list[str]] = ["zfab"]

    def process(self, instance: pyblish.api.Instance) -> None:
        """Process the instance to extract zfab data."""
        stagingdir = self.staging_dir(instance)
        filename = f"{instance.name}.zfab"
        filepath = os.path.join(stagingdir, filename)
        target_fabric_index = instance.data["fabricIndex"]

        fabric_api.ExportZFab(filepath, target_fabric_index)

        rep = Representation("zfab file", traits=[
            FileLocation(
                file_path=Path(stagingdir) / filename),
            Static(),
            Persistent(),
        ])
        add_trait_representations(
            instance,
            [rep],
        )

        self.log.info(
            "Extracted instance '%: %s' to: %s",
            instance.name,
            rep.name,
            rep.get_trait(FileLocation).file_path,
        )
