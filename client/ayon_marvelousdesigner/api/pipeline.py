# -*- coding: utf-8 -*-
"""Pipeline tools for Ayon Substance Designer integration."""
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
    register_loader_plugin_path,
    register_creator_plugin_path,
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
    name = "marvelousdesigner"

    def __init__(self):
        super(MarvelousDesignerHost, self).__init__()
        self._has_been_setup = False
        self.callbacks = []
        self.shelves = []

    @staticmethod
    def show_tools_dialog():
        """Show tools dialog with actions leading to show other tools."""
        show_tools_dialog()

    def install(self):
        pyblish.api.register_host("marvelousdesigner")

        pyblish.api.register_plugin_path(str(PUBLISH_PATH))
        register_loader_plugin_path(str(LOAD_PATH))
        register_creator_plugin_path(str(CREATE_PATH))

        self._has_been_setup = True

    def workfile_has_unsaved_changes(self):
        # API not supported for the check
        return False

    def get_workfile_extensions(self):
        # support .sbsar and .sbsasm for read-only
        return [".zprj"]

    def save_workfile(self, dst_path=None):
        filepath = save_workfile(dst_path)
        return filepath

    def open_workfile(self, filepath):
        open_workfile(filepath)

    def get_current_workfile(self):
        return utility_api.GetProjectFilePath()

    def get_containers(self):
        return ls()

    def update_context_data(self, data, changes):
        set_metadata(AYON_CONTEXT_DATA, data)

    def get_context_data(self):
        metadata = get_ayon_metadata() or {}
        return metadata.get(AYON_CONTEXT_DATA, {})


def containerise(filename, name, namespace, context, loader):
    """Imprint a loaded container with metadata.

    Containerisation enables a tracking of version, author and origin
    for loaded assets.

    Arguments:
        name (str): Name of resulting assembly
        namespace (str): Namespace under which to host container
        context (dict): Asset information
        loader (load.LoaderPlugin): loader instance used to produce container.
        identifier (str): SDResource identifier
        options (dict): options

    Returns:
        None

    """
    data = {
        "schema": "ayon:container-3.0",
        "id": AYON_CONTAINER_ID,
        "name": str(name),
        "namespace": str(namespace) if namespace else None,
        "loader": str(loader.__class__.__name__),
        "representation": context["representation"]["id"],
        "project_name": context["project"]["name"],
        "objectName": filename
    }
    # save the main_data in a temp folder
    container_data = ls() or []
    container_data.append(data)
    set_metadata(AYON_CONTAINERS, container_data)


def get_current_workfile():
    """Get the current file path from the host."""
    host = registered_host()
    return host.get_current_workfile()


def get_ayon_metadata():
    """get AYON relevant metadata from current file

    Returns:
        str : json string for meta data [key - value] list
    """
    # need to convert string to dict
    metadata_str = utility_api.GetMetaDataForCurrentGarment()
    return json.loads(metadata_str)


def get_instances():
    """Retrieve all stored instances from the project settings."""
    ayon_metadata = get_ayon_metadata()
    return ayon_metadata.get(AYON_INSTANCES, {})


def get_instances_values():
    """Retrieve all stored instances from the project settings."""
    ayon_instances = get_instances()
    return list(ayon_instances.values())


def ls():
    """List all AYON containers in the current file metadata."""
    ayon_metadata = get_ayon_metadata() or {}
    return ayon_metadata.get(AYON_CONTAINERS, [])


def set_metadata(data_type: str, data: Union[dict, list]):
    """Set instance data into the current file metadata."""
    ayon_metadata = get_ayon_metadata()
    ayon_metadata[data_type] = data
    # Serialize with optional formatting
    json_to_str_data = f"{json.dumps(ayon_metadata)}"
    utility_api.SetMetaDataForCurrentGarment(json_to_str_data)


def set_instance(instance_id, instance_data, update=False):
    """Set a single instance into the current file metadata."""
    set_instances({instance_id: instance_data}, update=update)


def set_instances(instance_data_by_id, update=False):
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


def remove_instance(instance_id):
    """Helper method to remove the data for a specific container"""
    instances = get_instances()
    instances.pop(instance_id, None)
    set_metadata(AYON_INSTANCES, instances)


def save_workfile(filepath):
    export_api.ExportZPrj(filepath)
    open_workfile(filepath)
    return filepath


def open_workfile(filepath):
    import_options = ApiTypes.ImportZPRJOption()
    import_api.ImportZprj(filepath, import_options)
