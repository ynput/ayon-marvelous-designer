from ayon_marvelousdesigner.api import plugin


class CreateModel(plugin.MDCreator):
    """Model creator for Marvelous Designer."""
    identifier = "io.ayon.creators.marvelousdesigner.model"
    label = "Model"
    product_type = "model"
    product_base_type = "model"
    icon = "cube"
