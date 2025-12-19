# -*- coding: utf-8 -*-
"""Collect current work file."""
import pyblish.api
from ayon_core.lib import BoolDef, UISeparatorDef, UILabelDef
from ayon_core.pipeline.publish import AYONPyblishPluginMixin


class CollectExportOption(pyblish.api.InstancePlugin,
                          AYONPyblishPluginMixin):
    """Inject the current export option into context"""

    order = pyblish.api.CollectorOrder - 0.01
    label = "Collect Export Option"
    hosts = ['marvelousdesigner']
    families = ["model", "pointcache"]

    def process(self, instance):
        """Inject the current export option."""
        attr_values = self.get_attr_values_from_data(instance.data)
        export_option_data = {
            "bExportGarment": attr_values.get("bExportGarment", True),
            "bExportAvatar": attr_values.get("bExportAvatar", False),
            "bSingleObject": attr_values.get("bSingleObject", True),
            "bThin": attr_values.get("bThin", False),
            "bMetaData": attr_values.get("bMetaData", True),
        }
        instance.data["exportOptions"] = export_option_data

    @classmethod
    def get_attribute_defs(cls) -> list[BoolDef]:
        """Get attribute definitions for export options.
        
        Returns:
        list: List of boolean attribute definitions for export options.

        """
        return [
            UISeparatorDef("sep_export_options"),
            UILabelDef("Export Options"),
            BoolDef("bExportGarment",
                    label="Export Garment",
                    default=True),
            BoolDef("bExportAvatar",
                    label="Export Avatar",
                    default=False),
            BoolDef("bSingleObject",
                    label="Single Object",
                    default=True),
            BoolDef("bThin",
                    label="Thin",
                    default=False),
            BoolDef("bMetaData",
                    label="XML MetaData",
                    default=True),
            UISeparatorDef("sep_export_options"),
        ]
