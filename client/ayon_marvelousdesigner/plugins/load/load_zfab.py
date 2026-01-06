"""Plugin to load ZFab files into Marvelous Designer."""
import os
from typing import ClassVar, Optional, Union

import fabric_api
from ayon_core.pipeline import load
from ayon_marvelousdesigner.api.pipeline import (
    containerise,
    imprint,
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
        filepath = self.filepath_from_context(context)
        fabric_index = fabric_api.AddFabric(filepath)
        containerise(
            name=name,
            namespace=namespace,
            context=context,
            loader=self,
            options={"fabricIndex": fabric_index}
        )

    def update(self, container: dict, context: dict) -> None:
        """Update loaded zfab in the scene."""
        repre_entity = context["representation"]
        filepath = self.filepath_from_context(context)
        fabric_index = container.get("fabricIndex")
        if fabric_index is not None:
            fabric_api.ReplaceFabric(fabric_index, filepath)
        imprint(container["objectName"], {
            "filename": os.path.basename(filepath),
            "representation": repre_entity["id"],
        })


    def remove(self, container: dict) -> None:
        """Remove loaded zfab from the scene."""
        fabric_index = container.get("fabricIndex")
        if fabric_index is not None:
            fabric_api.DeleteFabric(fabric_index)

        remove_container_data(container["objectName"])
