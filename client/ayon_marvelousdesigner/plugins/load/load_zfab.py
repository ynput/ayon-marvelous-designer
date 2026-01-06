"""Plugin to load ZFab files into Marvelous Designer."""
from __future__ import annotations

import json
from pathlib import Path
from typing import ClassVar, Optional

import fabric_api
from ayon_core.pipeline import load
from ayon_core.pipeline.traits import (
    FileLocation,
    Representation,
)
from ayon_marvelousdesigner.api.pipeline import (
    containerise,
    imprint,
    remove_container_data,
    remove_container_data,
)


class LoadZfab(load.LoaderPlugin):
    """Load ZFab for project."""
    product_types: ClassVar[set[str]] = {"zfab"}
    representations: ClassVar[set[str]] = {"zfab"}

    label = "Load ZFab"
    order = -10
    icon = "code-fork"
    color = "orange"

    def load(
            self,
            context: dict,
            name: Optional[str] = None,
            namespace: Optional[str] = None,
            options: Optional[dict] = None) -> None:
        """Load pointcache into the scene.

        Args:
            context (dict): Context dictionary with representation info.
            name (str): Name of the container.
            namespace (str): Namespace for the loaded data.
            options (dict): Additional options for loading.

        """
        file_path = self._get_filepath(context)

        fabric_index = fabric_api.AddFabric(file_path.as_posix())
        containerise(
            name=name,
            namespace=namespace,
            context=context,
            loader=self,
            options={"fabricIndex": fabric_index}
        )

    def update(self, container: dict, context: dict) -> None:
        """Update loaded zfab in the scene.

        Args:
            container (dict): Container data.
            context (dict): Context dictionary with representation info.

        """
        file_path = self._get_filepath(context)

        fabric_index = container.get("fabricIndex")
        if fabric_index is not None:
            fabric_api.ReplaceFabric(fabric_index, file_path.as_posix())
        imprint(container["objectName"], {
            "representation": context["representation"]["id"],
        })

    def remove(self, container: dict) -> None:
        """Remove loaded zfab from the scene."""
        fabric_index = container.get("fabricIndex")
        if fabric_index is not None:
            fabric_api.DeleteFabric(fabric_index)

        remove_container_data(container["objectName"])

    def _get_filepath(self, context: dict) -> Path:
        """Gets filepath with either representation trait or context data.

        For backward compatibility only.

        Args:
            context (dict): Context dictionary.

        Returns:
            Path: File path to load.

        """
        traits_raw = context["representation"].get("traits")
        if traits_raw is not None:
            # construct Representation object from the context
            representation = Representation.from_dict(
                name=context["representation"]["name"],
                representation_id=context["representation"]["id"],
                trait_data=json.loads(traits_raw),
            )

            file_path: Path = representation.get_trait(FileLocation).file_path
        else:
            filepath = self.filepath_from_context(context)
            file_path = Path(filepath)

        return file_path
