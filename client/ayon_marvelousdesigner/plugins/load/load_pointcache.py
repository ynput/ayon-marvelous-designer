
"""Point cache loader plugin for Marvelous Designer integration.

This module provides LoadPointCache class for loading various point cache formats
(ABC, FBX, OBJ) into Marvelous Designer through the AYON pipeline.
"""

import os
from typing import Union
import import_api
import ApiTypes
from ayon_core.pipeline import load
from ayon_core.pipeline.load import LoadError
from ayon_marvelousdesigner.api.pipeline import containerise


class LoadPointCache(load.LoaderPlugin):
    """Load Pointcache for project"""

    product_types = {"*"}
    representations = {"abc", "fbx", "obj"}

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
            name=name,
            namespace=namespace,
            context=context,
            loader=self
        )

    @staticmethod
    def load_pointcache(
        filepath: str,
        extension: str,
        options: Union[ApiTypes.ImportAlembicOption,
                       ApiTypes.ImportExportOption]) -> None:
        """Actual loading logic for pointcache.

        Args:
            filepath (str): Path to pointcache file.
            extension (str): Extension of pointcache file.
            options (ApiTypes.ImportExportOption): Options for loading.

        Raises:
            LoaderError: If the pointcache format is unsupported.
        """
        if extension == ".abc":
            import_api.ImportAlembic(filepath, options)
        elif extension == ".fbx":
            import_api.ImportFBX(filepath, options)
        elif extension == ".obj":
            import_api.ImportOBJ(filepath, options)
        else:
            raise LoadError(
                f"Unsupported pointcache format: {extension}"
            )

    @staticmethod
    def load_options(extension: str) -> Union[
            ApiTypes.ImportAlembicOption, ApiTypes.ImportExportOption]:
        """Return options for loading pointcache.
        
        Raises:
            LoaderError: If the pointcache format is unsupported.
        """
        if extension == ".abc":
            return ApiTypes.ImportAlembicOption()

        if extension in {".fbx", ".obj"}:
            return ApiTypes.ImportExportOption()

        raise LoadError(
            f"Unsupported pointcache format: {extension}"
        )
