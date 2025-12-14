import os
import pyblish.api
import export_api
import ApiTypes
from ayon_core.pipeline import publish, OptionalPyblishPluginMixin
from ayon_core.pipeline.publish import KnownPublishError


class ExtractModel(publish.Extractor, OptionalPyblishPluginMixin):
    """Extract Geometry in Alembic Format."""

    order = pyblish.api.ExtractorOrder - 0.05
    label = "Extract Model (Alembic)"
    hosts = ["marvelousdesigner"]
    families = ["model"]
    optional = True
    extension = "abc"

    settings_category = "max"

    def process(self, instance):
        if not self.is_active(instance.data):
            return

        stagingdir = self.staging_dir(instance)
        filename = f"{instance.name}.{self.extension}"
        filepath = os.path.join(stagingdir, filename)
        export_options = ApiTypes.ImportExportOption()
        output_file = self._export_mesh(filepath, export_options)
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


class ExtractModelObj(ExtractModel):
    """Extract Geometry in OBJ Format."""

    label = "Extract Model (OBJ)"
    extension = "obj"

    @staticmethod
    def _export_mesh(
            filepath: str,
            export_options: ApiTypes.ImportExportOption
        ) -> str:
        return export_api.ExportOBJ(filepath, export_options)


class ExtractModelFbx(ExtractModel):
    """Extract Geometry in FBX Format."""

    label = "Extract Model (FBX)"
    extension = "fbx"

    @staticmethod
    def _export_mesh(
            filepath: str,
            export_options: ApiTypes.ImportExportOption
        ) -> str:
        return export_api.ExportFBX(filepath, export_options)
