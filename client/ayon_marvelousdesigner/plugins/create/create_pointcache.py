"""Create Point Cache plugin for Marvelous Designer.

This module contains the CreatePointCache class for creating point cache
products in Marvelous Designer within the AYON pipeline.
"""

from ayon_marvelousdesigner.api import plugin


class CreatePointCache(plugin.MDCreator):
    """Model creator for Marvelous Designer."""
    identifier = "io.ayon.creators.marvelousdesigner.pointcache"
    label = "Point Cache"
    product_base_type = "pointcache"
    product_type = product_base_type
    icon = "pagelines"
