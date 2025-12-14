import os
import import_api
import ApiTypes
from ayon_core.pipeline import load
from ayon_core.pipeline.load import LoaderError
from ayon_marvelousdesigner.api.pipeline import containerise


class LoadPointCache(load.LoaderPlugin):
    """Load Pointcache for project"""

    product_types = {"pointcache", "model"}
    representations = {"*"}

    label = "Load Pointcache"
    order = -10
    icon = "code-fork"
    color = "orange"

    def load(self, context, name, namespace, options):
        """Load pointcache into the scene."""
        filepath = self.filepath_from_context(context)
        extension = os.path.splitext(filepath)[-1].lower()
        loaded_options = self.load_options(extension)
        self.load_pointcache(filepath, extension, loaded_options)
        containerise(
            filename=os.path.basename(filepath),
            name=name,
            namespace=namespace,
            context=context,
            loader=self
        )

    def load_pointcache(self, filepath, extension, options):
        """Actual loading logic for pointcache."""
        if extension == ".abc":
            import_api.ImportAlembic(filepath, options)
        elif extension == ".fbx":
            import_api.ImportFBX(filepath, options)
        elif extension == ".obj":
            import_api.ImportOBJ(filepath, options)
        else:
            raise LoaderError(
                f"Unsupported pointcache format: {extension}"
            )

    def load_options(self, extension):
        """Return options for loading pointcache."""
        if extension == ".abc":
            return ApiTypes.ImportAlembicOption()
        elif extension == ".fbx" or extension == ".obj":
            return ApiTypes.ImportExportOption()
        else:
            raise LoaderError(
                f"Unsupported pointcache format: {extension}"
            )
