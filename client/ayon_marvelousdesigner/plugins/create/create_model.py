"""Create plugin for Marvelous Designer model product type."""

from ayon_marvelousdesigner.api import plugin


class CreateModel(plugin.MDCreator):
    """Model creator for Marvelous Designer."""
    identifier = "io.ayon.creators.marvelousdesigner.model"
    label = "Model"
    product_base_type = "model"
    product_type = product_base_type
    icon = "cube"
