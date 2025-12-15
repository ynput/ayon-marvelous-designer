from ayon_marvelousdesigner.api import plugin


class CreateZFab(plugin.MDCreator):
    """Model creator for Marvelous Designer."""
    identifier = "io.ayon.creators.marvelousdesigner.zfab"
    label = "Zfab"
    product_type = "zfab"
    product_base_type = "zfab"
    icon = "picture-o"
