"""Pipeline tools for Ayon Substance Designer integration."""
from __future__ import annotations

import json
import logging
import os
from typing import Union

# Marvelous Designer modules
import ApiTypes
import export_api
import import_api
import pyblish.api
import utility_api

# Ayon Core modules
from ayon_core.host import HostBase, ILoadHost, IPublishHost, IWorkfileHost
from ayon_core.pipeline import (
    AYON_CONTAINER_ID,
    register_creator_plugin_path,
    register_loader_plugin_path,
    registered_host,
)

# Ayon Marvelous Designer modules
from ayon_marvelousdesigner import MARVELOUS_DESIGNER_HOST_DIR
from ayon_marvelousdesigner.api.ayon_dialog import show_tools_dialog

log = logging.getLogger("ayon_marvelousdesigner")

PLUGINS_DIR = os.path.join(MARVELOUS_DESIGNER_HOST_DIR, "plugins")
PUBLISH_PATH = os.path.join(PLUGINS_DIR, "publish")
LOAD_PATH = os.path.join(PLUGINS_DIR, "load")
CREATE_PATH = os.path.join(PLUGINS_DIR, "create")

# AYON metadata keys
AYON_ATTRIBUTE = "ayon"
AYON_INSTANCES = "ayon_instances"
AYON_CONTAINERS = "ayon_containers"
AYON_CONTEXT_DATA = "ayon_context_data"


class MarvelousDesignerHost(HostBase, IWorkfileHost, ILoadHost, IPublishHost):
    """Host class for Marvelous Designer integration with AYON pipeline.

    This class provides the main interface between AYON and Marvelous Designer,
    implementing workfile operations, loading, and publishing functionality.

    Attributes:
        name (str): The host name identifier.
        _has_been_setup (bool): Flag indicating if the host has been initialized.
        callbacks (list): List of registered callbacks.
        shelves (list): List of UI shelves.
    """
    name = "marvelousdesigner"

    def __init__(self):
        """Initialize the Marvelous Designer host with default settings."""
        super().__init__()
        self._has_been_setup = False
        self.callbacks = []
        self.shelves = []

    @staticmethod
    def show_tools_dialog() -> None:
        """Show tools dialog with actions leading to show other tools."""
        show_tools_dialog()

    def install(self) -> None:
        """Install and register the MD host with Ayon pipeline."""
        pyblish.api.register_host("marvelousdesigner")

        pyblish.api.register_plugin_path(str(PUBLISH_PATH))
        register_loader_plugin_path(str(LOAD_PATH))
        register_creator_plugin_path(str(CREATE_PATH))

        self._has_been_setup = True

    def workfile_has_unsaved_changes(self) -> bool:  # noqa: PLR6301
        """Check if the current workfile has unsaved changes.

        Returns:
            bool: True if there are unsaved changes, False otherwise.
        """
        # API not supported for the check
        return utility_api.CheckZPRJForUnsavedChanges()

    def get_workfile_extensions(self) -> list[str]:  # noqa: PLR6301
        """Get the list of supported workfile extensions.

        Returns:
            list[str]: List of supported workfile extensions.
        """
        return [".zprj"]

    def save_workfile(self, dst_path: str | None = None) -> str | None:  # noqa: PLR6301
        """Save the current workfile to the specified destination path.

        Args:
            dst_path (str | None, optional): Destination path to save
                the workfile. Defaults to None.

        Returns:
            str | None: The path where the workfile was saved, or None
            if saving failed.
        """
        save_workfile(dst_path)
        return dst_path

    def open_workfile(self, filepath: str) -> None:  # noqa: PLR6301
        """Open a workfile from the specified file path."""
        open_workfile(filepath)

    def get_current_workfile(self) -> str:  # noqa: PLR6301
        """Get the current workfile path from the host.

        Returns:
            str: The current workfile path.
        """
        return utility_api.GetProjectFilePath()

    def get_containers(self) -> list:  # noqa: PLR6301
        """Get the list of containers in the current scene.

        Returns:
            list: List of container metadata dictionaries.
        """
        return ls()

    def update_context_data(self, data: dict, changes: dict) -> None:  # noqa : PLR6301
        """Update the context data in the current file metadata."""
        # Note: 'changes' parameter is part of the interface but not used in MD
        _ = changes  # Explicitly ignore the unused parameter
        set_metadata(AYON_CONTEXT_DATA, data)

    def get_context_data(self) -> dict:  # noqa: PLR6301
        """Get the context data from the current file metadata.

        Returns:
            dict: Context data dictionary.
        """
        metadata = get_ayon_metadata() or {}
        return metadata.get(AYON_CONTEXT_DATA, {})


def containerise(
        name: str, namespace: str,
        context: dict, loader: object,
        options: dict | None = None) -> None:
    """Imprint a loaded container with metadata.

    Containerisation enables a tracking of version, author and origin
    for loaded assets.

    Arguments:
        name (str): Name of resulting assembly
        namespace (str): Namespace under which to host container
        context (dict): Asset information
        loader (load.LoaderPlugin): loader instance used to produce container.
        options (dict): options

    """
    data = {
        "schema": "ayon:container-3.0",
        "id": AYON_CONTAINER_ID,
        "name": str(name),
        "namespace": str(namespace) if namespace else None,
        "loader": str(loader.__class__.__name__),
        "representation": context["representation"]["id"],
        "project_name": context["project"]["name"],
        "objectName": name,
    }
    if options:
        fabric_index = options.get("fabricIndex")
        data["fabricIndex"] = fabric_index
        data["objectName"] = f"{name}_fabric_{fabric_index}"
    else:
        data["objectName"] = name
    # save the main_data in a temp folder
    container_data = ls() or []
    container_data.append(data)
    set_metadata(AYON_CONTAINERS, container_data)


def imprint(object_name: str, data: dict) -> None:
    """Imprint metadata onto an object in the scene.

    Args:
        object_name (str): Name of the object to imprint metadata on.
        data (dict): Metadata to imprint.
    """
    # Retrieve existing containers
    container_data = ls()
    # Find the container for the specified object
    for container in container_data:
        if container.get("objectName") == object_name:
            container.update(data)
            break
    else:
        log.warning(
            "No container found for object %s to imprint data.", object_name
        )
        return
    # Update the metadata
    set_metadata(AYON_CONTAINERS, container_data)


def remove_container_data(object_name: str) -> None:
    """Remove container data for a specific object in the scene.

    Args:
        object_name (str): Name of the object whose container data is to
            be removed.
    """
    container_data = ls()
    # Filter out the container for the specified object
    updated_containers = [
        container for container in container_data
        if container.get("objectName") != object_name
    ]
    # Update the metadata
    set_metadata(AYON_CONTAINERS, updated_containers)


def get_current_workfile() -> str:
    """Get the current file path from the host.

    Returns:
        str: The current workfile path.
    """
    host = registered_host()
    return host.get_current_workfile()


def get_ayon_metadata() -> dict:
    """Get AYON relevant metadata from current file.

    Returns:
        dict: AYON metadata as a dictionary.
    """
    # need to convert string to dict
    metadata_str = utility_api.GetMetaDataForCurrentGarment()
    return json.loads(metadata_str)


def get_instances() -> dict:
    """Retrieve all stored instances from the project settings.

    Returns:
        dict: Dictionary of stored instances from the project settings.
    """
    ayon_metadata = get_ayon_metadata()
    return ayon_metadata.get(AYON_INSTANCES, {})


def get_instances_values() -> list:
    """Retrieve all stored instances from the project settings.
    
    Returns:
        list: List of all instance values from the project settings.
    """
    ayon_instances = get_instances()
    return list(ayon_instances.values())


def ls() -> list:
    """List all AYON containers in the current file metadata.

    Returns:
        list: List of AYON container metadata dictionaries.
    """
    ayon_metadata = get_ayon_metadata() or {}
    return ayon_metadata.get(AYON_CONTAINERS, [])


def set_metadata(data_type: str, data: Union[dict, list]) -> None:
    """Set instance data into the current file metadata."""
    ayon_metadata = get_ayon_metadata()
    ayon_metadata[data_type] = data
    # Serialize with optional formatting
    json_to_str_data = f"{json.dumps(ayon_metadata)}"
    utility_api.SetMetaDataForCurrentGarment(json_to_str_data)


def set_instance(
    instance_id: str, instance_data: dict, *, update: bool = False) -> None:
    """Set a single instance into the current file metadata."""
    set_instances({instance_id: instance_data}, update=update)


def set_instances(instance_data_by_id: dict, *, update: bool = False) -> None:
    """Set multiple instances into the current file metadata.

    Args:
        instance_data_by_id (dict): instance data mapped by their IDs
        update (bool, optional): Whether to update existing instances.
        Defaults to False.
    """
    instances = get_instances()
    for instance_id, instance_data in instance_data_by_id.items():
        if update:
            existing_data = instances.get(instance_id, {})
            existing_data.update(instance_data)
        else:
            instances[instance_id] = instance_data

    set_metadata(AYON_INSTANCES, instances)


def remove_instance(instance_id: str) -> None:
    """Helper method to remove the data for a specific container."""
    instances = get_instances()
    instances.pop(instance_id, None)
    set_metadata(AYON_INSTANCES, instances)


def save_workfile(filepath: str) -> None:
    """Save the current workfile to the specified file path."""
    export_api.ExportZPrj(filepath)
    open_workfile(filepath)


def open_workfile(filepath: str) -> None:
    """Open a workfile from the specified file path."""
    import_options = ApiTypes.ImportZPRJOption()
    import_api.ImportZprj(filepath, import_options)
