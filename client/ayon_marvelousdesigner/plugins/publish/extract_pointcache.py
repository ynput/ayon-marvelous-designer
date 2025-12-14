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
    families = ["model", "pointcache"]
    optional = True
    extension = "abc"

    settings_category = "marvelousdesigner"

    def process(self, instance):
        if not self.is_active(instance.data):
            return

        stagingdir = self.staging_dir(instance)
        filename = f"{instance.name}.{self.extension}"
        filepath = os.path.join(stagingdir, filename)
        export_option = ApiTypes.ImportExportOption()
        export_option.bExportGarment = True
        export_option.bExportAvatar = False
        export_option.bSingleObject = True
        export_option.bExportAnimation = (
            instance.data["productType"] != "model"
        )

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

    @staticmethod
    def _export_mesh(
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
        return export_api.ExportAlembic(filepath, export_options)


class ExtractPointCacheObj(ExtractPointCache):
    """Extract Geometry in OBJ Format."""

    label = "Extract Model (OBJ)"
    families = ["model"]
    extension = "obj"

    @staticmethod
    def _export_mesh(
            filepath: str,
            export_options: ApiTypes.ImportExportOption
        ) -> str:
        return export_api.ExportOBJ(filepath, export_options)


class ExtractFbx(ExtractPointCache):
    """Extract Geometry in FBX Format."""

    label = "Extract PointCache (FBX)"
    families = ["model", "pointcache"]
    extension = "fbx"

    @staticmethod
    def _export_mesh(
            filepath: str,
            export_options: ApiTypes.ImportExportOption
        ) -> str:
        return export_api.ExportFBX(filepath, export_options)
