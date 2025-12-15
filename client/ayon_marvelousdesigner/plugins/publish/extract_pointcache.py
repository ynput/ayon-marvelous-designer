import os
import pyblish.api
import export_api
import ApiTypes
from ayon_core.pipeline import publish, OptionalPyblishPluginMixin
from ayon_core.pipeline.publish import KnownPublishError


class ExtractPointCache(publish.Extractor, OptionalPyblishPluginMixin):
    """Extract Geometry in Alembic Format."""

    order = pyblish.api.ExtractorOrder - 0.05
    label = "Extract PointCache (Alembic)"
    hosts = ["marvelousdesigner"]
    families = ["pointcache", "model"]
    optional = True
    extension = "abc"

    settings_category = "marvelousdesigner"

    def process(self, instance):
        if not self.is_active(instance.data):
            return

        stagingdir = self.staging_dir(instance)
        filename = f"{instance.name}.{self.extension}"
        xml_filename = f"{instance.name}.xml"
        filepath = os.path.join(stagingdir, filename)
        xml_output = os.path.join(stagingdir, xml_filename)
        export_option = self.export_option()

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

    @staticmethod
    def export_option() -> ApiTypes.ImportExportOption:
        """Get export options for point cache export.

        Returns:
            ApiTypes.ImportExportOption: export options
        """
        export_option = ApiTypes.ImportExportOption()
        export_option.bExportGarment = True
        export_option.bExportAvatar = False
        export_option.bSingleObject = True
        export_option.bThin = False
        export_option.bMetaData = True
        return export_option


class ExtractModel(ExtractPointCache):
    """Extract Model in Obj Format."""

    label = "Extract Model (Obj)"
    families = ["model"]
    extension = "obj"

    @staticmethod
    def export_option() -> ApiTypes.ImportExportOption:
        """Get export options for point cache export.

        Returns:
            ApiTypes.ImportExportOption: export options
        """
        export_option = ApiTypes.ImportExportOption()
        export_option.bExportGarment = True
        export_option.bExportAvatar = False
        export_option.bSingleObject = False
        export_option.bThin = True
        export_option.bMetaData = False
        return export_option


class ExtractModelThick(ExtractPointCache):
    """Extract Geometry in Obj Format."""

    label = "Extract Model Thick (Obj)"
    families = ["model"]
    extension = "obj"

    @staticmethod
    def export_option() -> ApiTypes.ImportExportOption:
        """Get export options for point cache export.

        Returns:
            ApiTypes.ImportExportOption: export options
        """
        export_option = ApiTypes.ImportExportOption()
        export_option.bExportGarment = True
        export_option.bExportAvatar = False
        export_option.bSingleObject = True
        export_option.bThin = False
        export_option.bMetaData = False
        return export_option


class ExtractModelPanel(ExtractPointCache):
    """Extract Geometry in Obj Format."""

    label = "Extract Model 2D Panel (Obj)"
    families = ["model"]
    extension = "obj"

    @staticmethod
    def export_option() -> ApiTypes.ImportExportOption:
        """Get export options for point cache export.

        Returns:
            ApiTypes.ImportExportOption: export options
        """
        export_option = ApiTypes.ImportExportOption()
        export_option.bExportGarment = True
        export_option.bExportAvatar = False
        export_option.bSingleObject = True
        export_option.bThin = False
        export_option.bMetaData = False
        return export_option


class ExtractPointCacheObj(ExtractPointCache):
    """Extract PointCache in OBJ Format."""

    label = "Extract PointCache (OBJ)"
    families = ["pointcache"]
    extension = "obj"


class ExtractFbx(ExtractPointCache):
    """Extract Geometry in FBX Format."""

    label = "Extract PointCache (FBX)"
    families = ["model", "pointcache"]
    extension = "fbx"
