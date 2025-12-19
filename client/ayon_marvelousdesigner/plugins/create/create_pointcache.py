from ayon_marvelousdesigner.api import plugin


class CreatePointCache(plugin.MDCreator):
    """Model creator for Marvelous Designer."""
    identifier = "io.ayon.creators.marvelousdesigner.pointcache"
    label = "Point Cache"
    product_type = "pointcache"
    product_base_type = "pointcache"
    icon = "pagelines"
