"""Server package."""
from typing import Type

from ayon_server.addons import BaseServerAddon

from .settings import DEFAULT_MD_VALUES, MarvelousDesignerSettings


class MarvelousDesignerAddon(BaseServerAddon):
    """Add-on class for the server."""
    settings_model: Type[MarvelousDesignerSettings] = MarvelousDesignerSettings

    async def get_default_settings(self) -> MarvelousDesignerSettings:
        """Return default settings."""
        settings_model_cls = self.get_settings_model()
        return settings_model_cls(**DEFAULT_MD_VALUES)
