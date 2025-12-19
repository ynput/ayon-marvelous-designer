from ayon_marvelousdesigner.api import plugin


class CreateZFab(plugin.MDCreator):
    """Model creator for Marvelous Designer."""
    identifier = "io.ayon.creators.marvelousdesigner.zfabSet"
    label = "Zfab"
    product_type = "zfabSet"
    product_base_type = "zfabSet"
    icon = "picture-o"
