
"""Creator plugin for Marvelous Designer Zfab products.

This module provides the CreateZFab creator class for generating
zfab product instances in Marvelous Designer.
"""

# Marvelous Designer Module API
import fabric_api
from ayon_core.lib import BoolDef
from ayon_marvelousdesigner.api import plugin
from ayon_marvelousdesigner.api.pipeline import set_instance


class CreateZFab(plugin.MDCreator):
    """Model creator for Marvelous Designer."""
    identifier = "io.ayon.creators.marvelousdesigner.zfab"
    label = "Zfab"
    product_type = "zfab"
    product_base_type = "zfab"
    icon = "picture-o"

    def create(self, product_name: str,
               instance_data: dict, pre_create_data: dict) -> None:
        """Create a new zfab product instance in Marvelous Designer.

        Args:
        product_name(str): The name of the product to create.
        instance_data(dict): Data associated with the instance.
        pre_create_data(dict): Pre-creation configuration data.
        """
        if pre_create_data.get("use_selection"):
            instance_data["fabricIndex"] = fabric_api.GetCurrentFabricIndex()
        else:
            instance_data["fabricIndex"] = 1

        instance = self.create_instance_in_context(product_name,
                                                   instance_data)

        set_instance(
            instance_id=instance["instance_id"],
            instance_data=instance.data_to_store()
        )

    @staticmethod
    def get_pre_create_attr_defs() -> list:
        """Get pre-creation attribute definitions.

        Returns:
            list: List of attribute definitions for pre-creation configuration.
        """
        return [
            BoolDef("use_selection", label="Use selection")
        ]
