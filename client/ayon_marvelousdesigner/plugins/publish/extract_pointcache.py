"""Plugin for extracting point cache data from Marvelous Designer.

This module provides extractors for exporting geometry and animation data
in various formats (Alembic, OBJ, FBX) from Marvelous Designer.
"""

import os
from typing import ClassVar, List

import ApiTypes
import export_api
import pyblish.api
from ayon_core.pipeline import OptionalPyblishPluginMixin, publish
from ayon_core.pipeline.publish import KnownPublishError


class ExtractPointCache(publish.Extractor, OptionalPyblishPluginMixin):
    """Extract Geometry in Alembic Format."""

    order = pyblish.api.ExtractorOrder - 0.05
    label = "Extract PointCache (Alembic)"
    hosts: ClassVar = ["marvelousdesigner"]
    families: ClassVar = ["model", "pointcache"]
    optional = True
    extension = "abc"

    def process(self, instance: pyblish.api.Instance) -> None:
        """Process the instance to extract point cache data.

        Args:
            instance (pyblish.api.Instance): The instance to process
            for extraction.

        Raises:
            KnownPublishError: If the output file wasn't produced by
            Marvelous Designer.
        """
        if not self.is_active(instance.data):
            return

        stagingdir = self.staging_dir(instance)
        filename = f"{instance.name}.{self.extension}"
        xml_filename = f"{instance.name}.xml"
        filepath = os.path.join(stagingdir, filename)
        xml_output = os.path.join(stagingdir, xml_filename)
        export_option = self.export_option(instance)

        output_file = self._export_mesh(filepath, export_option)
        if not os.path.exists(output_file):
            msg = (
                f"File {output_file} wasn't produced by Marvelous Designer, "
                "please check the logs."
            )
            raise KnownPublishError(
                msg
            )

        if "representations" not in instance.data:
            instance.data["representations"] = []

        representation = {
            "name": self.extension,
            "ext": self.extension,
            "files": filename,
            "stagingDir": stagingdir,
        }

        instance.data["representations"].append(representation)
        self.log.info(
            "Extracted instance '%s' to: %s" % (instance.name, filepath)
        )

        if os.path.exists(xml_output):
            xml_representation = {
                "name": "xml",
                "ext": "xml",
                "files": xml_filename,
                "stagingDir": stagingdir,
            }
            instance.data["representations"].append(xml_representation)
            self.log.info(
                "Extracted instance '%s' to: %s" % (instance.name, filepath)
            )

    def _export_mesh(
            self,
            filepath: str,
            export_options: ApiTypes.ImportExportOption
        ) -> str:
        """Export mesh to filepath.

        Args:
            filepath (str): filepath
            export_options (ApiTypes.ImportExportOption): export options

        Returns:
            str: Output file paths

        Raises:
            KnownPublishError: If the export format is not supported.
        """
        if self.extension == "abc":
            return export_api.ExportAlembic(filepath, export_options)
        if self.extension == "fbx":
            return export_api.ExportFBX(filepath, export_options)
        if self.extension == "obj":
            return export_api.ExportOBJ(filepath, export_options)

        raise KnownPublishError(
            f"Unsupported export format: {self.extension}"
        )

    def export_option(
            self, instance: pyblish.api.Instance
        ) -> ApiTypes.ImportExportOption:
        """Get export options for point cache export.

        Returns:
            ApiTypes.ImportExportOption: export options
        """
        export_option = ApiTypes.ImportExportOption()
        export_option.bExportAnimation = (
            instance.data["productBaseType"] == "pointcache"
        )
        options = instance.data["exportOptions"]
        export_option.bExportGarment = options.get("bExportGarment", True)
        export_option.bExportAvatar = options.get("bExportAvatar", False)
        export_option.bSingleObject = options.get("bSingleObject", True)
        export_option.bThin = options.get("bThin", False)
        export_option.bMetaData = options.get("bMetaData", True)
        return export_option


class ExtractObj(ExtractPointCache):
    """Extract PointCache in OBJ Format."""

    label = "Extract OBJ"
    extension = "obj"


class ExtractFbx(ExtractPointCache):
    """Extract Geometry in FBX Format."""

    label = "Extract FBX"
    extension = "fbx"
