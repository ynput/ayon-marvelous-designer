"""Settings for the addon."""
from typing import Any

from ayon_server.settings import (
    BaseSettingsModel,
    SettingsField,
)


class ProductTypeItemModel(BaseSettingsModel):
    _layout = "compact"
    product_type: str = SettingsField(
        title="Product type",
        description="Product type name"
    )
    label: str = SettingsField(
        "",
        title="Label",
        description="Label to show in UI for the product type"
    )


class BaseCreatePluginModel(BaseSettingsModel):
    product_type_items: list[ProductTypeItemModel] = SettingsField(
        default_factory=list,
        title="Product type items",
        description=(
            "Optional list of product types this plugin can create. "
        ),
    )


class CreatePluginsModel(BaseSettingsModel):
    CreateModel: BaseCreatePluginModel = SettingsField(
        title="Create Model",
        default_factory=BaseCreatePluginModel,
    )
    CreatePointCache: BaseCreatePluginModel = SettingsField(
        title="Create Point Cache",
        default_factory=BaseCreatePluginModel,
    )
    CreateZFab: BaseCreatePluginModel = SettingsField(
        title="Create Zfab",
        default_factory=BaseCreatePluginModel,
    )


class BasicValidateModel(BaseSettingsModel):
    """Basic model for publisher settings validation."""
    enabled: bool = SettingsField(title="Enabled")
    optional: bool = SettingsField(title="Optional")
    active: bool = SettingsField(title="Active")


class LoadPointCacheModel(BaseSettingsModel):
    """Model for Load Point Cache settings."""
    scale: float = SettingsField(
        default=1.0,
        title="Scale",
        description="Scale factor for loading point cache data."
    )


class PublishersModel(BaseSettingsModel):
    """Settings for publishers configuration."""
    ExtractPointCache: BasicValidateModel = SettingsField(
        default_factory=BasicValidateModel,
        title="Extract Point Cache"
    )
    ExtractObj: BasicValidateModel = SettingsField(
        default_factory=BasicValidateModel,
        title="Extract OBJ"
    )
    ExtractFbx: BasicValidateModel = SettingsField(
        default_factory=BasicValidateModel,
        title="Extract FBX"
    )


class LoadersModel(BaseSettingsModel):
    """Settings for loaders configuration."""
    LoadPointCache: LoadPointCacheModel = SettingsField(
        default_factory=LoadPointCacheModel,
        title="Load Point Cache"
    )


class PrelaunchModel(BaseSettingsModel):
    """Settings for prelaunch configuration."""
    qt_binding_dir: str = SettingsField(
        default="",
        title="Qt Binding Directory"
    )


class MarvelousDesignerSettings(BaseSettingsModel):
    """Settings for the Marvelous Designer addon."""
    prelaunch_settings: PrelaunchModel = SettingsField(
        default_factory=PrelaunchModel,
        title="Prelaunch Settings"
    )
    create: CreatePluginsModel = SettingsField(
        default_factory=CreatePluginsModel,
        title="Create"
    )
    publish: PublishersModel = SettingsField(
        default_factory=PublishersModel,
        title="Publishers"
    )
    load: LoadersModel = SettingsField(
        default_factory=LoadersModel,
        title="Loaders"
    )


DEFAULT_MD_VALUES: dict[str, Any] = {
    "prelaunch_settings": {
        "qt_binding_dir": "/Users/Public/Documents/MarvelousDesigner/Configuration/python311/Lib/site-packages",  # noqa: E501
    },
    "load": {
        "LoadPointCache": {
            "scale": 1.0
        }
    },
    "publish": {
        "ExtractPointCache": {
            "enabled": True,
            "optional": True,
            "active": True
        },
        "ExtractObj": {
            "enabled": True,
            "optional": True,
            "active": True
        },
        "ExtractFbx": {
            "enabled": True,
            "optional": True,
            "active": True
        },
    }
}
