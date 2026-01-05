"""Plugin for extracting point cache data from Marvelous Designer.

This module provides extractors for exporting geometry and animation data
in various formats (Alembic, OBJ, FBX) from Marvelous Designer.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import ClassVar

import ApiTypes
import export_api
import pyblish.api
from ayon_core.pipeline import OptionalPyblishPluginMixin, publish
from ayon_core.pipeline.publish import (
    KnownPublishError,
    add_trait_representations,
)
from ayon_core.pipeline.traits import (
    FileLocation,
    Geometry,
    Persistent,
    Representation,
    Spatial,
    Static,
    TraitValidationError,
)


class ExtractPointCache(publish.Extractor, OptionalPyblishPluginMixin):
    """Extract Geometry in Alembic Format."""

    order = pyblish.api.ExtractorOrder - 0.05
    label = "Extract PointCache (Alembic)"
    hosts: ClassVar[list[str]] = ["marvelousdesigner"]
    families: ClassVar[list[str]] = ["model", "pointcache"]
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
        filepath = Path(stagingdir) / filename

        xml_output = Path(stagingdir) / xml_filename
        export_option = self.export_option(instance)

        output_files = self._export_mesh(filepath.as_posix(), export_option)
        if not output_files:
            msg = (
                f"Files [{output_files}] wasn't produced by Marvelous "
                "Designer, please check the logs."
            )
            raise KnownPublishError(
                msg
            )
        up_axis = self.get_up_axis(export_option)
        rep = Representation(
            "pointcache",
            traits=[
                Static(),
                FileLocation(file_path=Path(stagingdir) / filename),
                Persistent(),
                Geometry(),
                Spatial(
                    up_axis=up_axis,
                    handedness="right",
                    meters_per_unit=export_option.scale / 100.0,
                ),
            ],
        )

        try:
            rep.validate()
        except TraitValidationError as e:
            msg = f"Representation {rep.name} is invalid: {e}"
            self.log.exception(msg)
        finally:
            add_trait_representations(instance, [rep])

        self.log.info(
            "Extracted instance '%: %s' to: %s",
            instance.name,
            rep.name,
            rep.get_trait(FileLocation).file_path)

        if os.path.exists(xml_output):

            xml_rep = Representation(
                "xml",
                traits=[
                    Static(),
                    FileLocation(file_path=Path(stagingdir) / xml_filename),
                    Persistent(),
                ],
            )

            try:
                rep.validate()
            except TraitValidationError as e:
                msg = f"Representation {xml_rep.name} is invalid: {e}"
                self.log.exception(msg)
            finally:
                add_trait_representations(instance, [xml_rep])

            self.log.info(
                "Extracted instance '%: %s' to: %s",
                instance.name,
                xml_rep.name,
                xml_rep.get_trait(FileLocation).file_path,
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
            return export_api.ExportAlembicW(filepath, export_options)
        if self.extension == "fbx":
            return export_api.ExportFBXW(filepath, export_options)
        if self.extension == "obj":
            return export_api.ExportOBJW(filepath, export_options)

        msg = f"Unsupported export format: {self.extension}"
        raise KnownPublishError(msg)

    @staticmethod
    def export_option(
            instance: pyblish.api.Instance
        ) -> ApiTypes.ImportExportOption:
        """Get export options for point cache export.

        Returns:
            ApiTypes.ImportExportOption: export options
        """
        export_option = ApiTypes.ImportExportOption()
        options = instance.data["exportOptions"]
        export_option.bExportGarment = options.get("bExportGarment", True)
        export_option.bExportAvatar = options.get("bExportAvatar", False)
        export_option.bSingleObject = options.get("bSingleObject", True)
        export_option.bThin = options.get("bThin", False)
        export_option.bMetaData = options.get("bMetaData", True)
        return export_option

    @staticmethod
    def get_up_axis(
            export_option: ApiTypes.ImportExportOption
        ) -> str:
        """Determine the up axis based on export options.

        Args:
            export_option (ApiTypes.ImportExportOption): Export options.

        Returns:
            str: The up axis ("Y" or "Z").
        """
        if export_option.axisY == 1:
            return "Y"
        if export_option.axisZ == 1:
            return "Z"
        if export_option.axisX == 1:
            return "X"
        return "Y"  # Default to Y if not specified


class ExtractObj(ExtractPointCache):
    """Extract PointCache in OBJ Format."""

    label = "Extract OBJ"
    extension = "obj"


class ExtractFbx(ExtractPointCache):
    """Extract Geometry in FBX Format."""

    label = "Extract FBX"
    extension = "fbx"
