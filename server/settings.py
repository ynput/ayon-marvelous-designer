"""Settings for the addon."""
from typing import Any

from ayon_server.settings import (
    BaseSettingsModel,
    SettingsField,
)


class BasicValidateModel(BaseSettingsModel):
    enabled: bool = SettingsField(title="Enabled")
    optional: bool = SettingsField(title="Optional")
    active: bool = SettingsField(title="Active")


class PublishersModel(BaseSettingsModel):
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


class MarvelousDesignerSettings(BaseSettingsModel):
    """Settings for the Marvelous Designer addon."""
    publish: PublishersModel = SettingsField(
        default_factory=PublishersModel,
        title="Publishers"
    )


DEFAULT_MD_VALUES: dict[str, Any] = {
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
