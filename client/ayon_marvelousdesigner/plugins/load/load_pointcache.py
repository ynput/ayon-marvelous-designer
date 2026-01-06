"""Point cache loader plugin for Marvelous Designer integration.

This module provides LoadPointCache class for loading various point cache formats
(ABC, FBX, OBJ) into Marvelous Designer through the AYON pipeline.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import ClassVar, Optional, Union

import ApiTypes
import import_api
from ayon_core.pipeline import load
from ayon_core.pipeline.load import LoadError
from ayon_core.pipeline.traits import (
    FileLocation,
    Representation,
)
from ayon_marvelousdesigner.api.pipeline import containerise


class LoadPointCache(load.LoaderPlugin):
    """Load Pointcache for project."""
    product_types: ClassVar[set[str]] = {"*"}
    representations: ClassVar[set[str]] = {"abc", "fbx", "obj"}

    label = "Load Pointcache"
    order = -10
    icon = "code-fork"
    color = "orange"

    def load(self,
             context: dict,
             name: Optional[str] = None,
             namespace: Optional[str] = None,
             options: Optional[dict] = None) -> None:
        """Load pointcache into the scene."""
        file_path = self._get_filepath(context)
        extension = file_path.suffix.lower()
        loaded_options = self.load_options(extension)
        self.load_pointcache(file_path.as_posix(), extension, loaded_options)
        containerise(
            name=name,
            namespace=namespace,
            context=context,
            loader=self
        )

    @staticmethod
    def load_pointcache(
        file_path: Path,
        extension: str,
        options: Union[ApiTypes.ImportAlembicOption,
                       ApiTypes.ImportExportOption]) -> None:
        """Actual loading logic for pointcache.

        Args:
            file_path (Path): Path to pointcache file.
            extension (str): Extension of pointcache file.
            options (ApiTypes.ImportExportOption): Options for loading.

        Raises:
            LoadError: If the pointcache format is unsupported.

        """
        if extension == ".abc":
            import_api.ImportAlembic(file_path, options)
        elif extension == ".fbx":
            import_api.ImportFBX(file_path, options)
        elif extension == ".obj":
            import_api.ImportOBJ(file_path, options)
        else:
            msg = f"Unsupported pointcache format: {extension}"
            raise LoadError(msg)
            msg = f"Unsupported pointcache format: {extension}"
            raise LoadError(msg)

    @staticmethod
    def load_options(extension: str) -> Union[
            ApiTypes.ImportAlembicOption, ApiTypes.ImportExportOption]:
        """Return options for loading pointcache.

        Args:
            extension (str): Extension of pointcache file.

        Returns:
            Union[
                ApiTypes.ImportAlembicOption,
                ApiTypes.ImportExportOption]: Options for loading.

        Raises:
            LoadError: If the pointcache format is unsupported.

        """
        if extension == ".abc":
            return ApiTypes.ImportAlembicOption()

        if extension in {".fbx", ".obj"}:
            return ApiTypes.ImportExportOption()

        msg = f"Unsupported pointcache format: {extension}"
        raise LoadError(msg)

    def _get_filepath(self, context: dict) -> Path:
        """Gets filepath with either representation trait or context data.

        For backward compatibility only.

        Args:
            context (dict): Context dictionary.

        Returns:
            Path: File path to load.

        """
        traits_raw = context["representation"].get("traits")
        if traits_raw is not None:
            # construct Representation object from the context
            representation = Representation.from_dict(
                name=context["representation"]["name"],
                representation_id=context["representation"]["id"],
                trait_data=json.loads(traits_raw),
            )

            file_path: Path = representation.get_trait(FileLocation).file_path
        else:
            filepath = self.filepath_from_context(context)
            file_path = Path(filepath)

        return file_path
