
import os
import fabric_api
from ayon_core.pipeline import load
from ayon_marvelousdesigner.api.pipeline import (
    containerise,
    imprint,
    remove_container_data
)


class LoadZfab(load.LoaderPlugin):
    """Load ZFab for project"""

    product_types = {"zfab"}
    representations = {"zfab"}

    label = "Load ZFab"
    order = -10
    icon = "code-fork"
    color = "orange"

    def load(self, context, name, namespace, options):
        """Load pointcache into the scene."""
        filepath = self.filepath_from_context(context)
        fabric_index = fabric_api.AddFabric(filepath)
        containerise(
            name=name,
            namespace=namespace,
            context=context,
            loader=self,
            options={"fabricIndex": fabric_index}
        )

    def update(self, container, context):
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


    def remove(self, container):
        """Remove loaded zfab from the scene."""
        fabric_index = container.get("fabricIndex")
        if fabric_index is not None:
            fabric_api.DeleteFabric(fabric_index)

        remove_container_data(container["objectName"])
