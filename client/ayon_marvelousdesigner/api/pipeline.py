# -*- coding: utf-8 -*-
"""Pipeline tools for Ayon Substance Designer integration."""
import json
import logging
import os

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
    registered_host,
)
from ayon_core.pipeline.context_tools import version_up_current_workfile
from ayon_core.settings import get_current_project_settings
# Ayon Marvelous Designer modules
from ayon_marvelousdesigner import MARVELOUS_DESIGNER_HOST_DIR
from ayon_marvelousdesigner.api.ayon_dialog import show_tools_dialog


log = logging.getLogger("ayon_marvelousdesigner")

PLUGINS_DIR = os.path.join(MARVELOUS_DESIGNER_HOST_DIR, "plugins")
PUBLISH_PATH = os.path.join(PLUGINS_DIR, "publish")
LOAD_PATH = os.path.join(PLUGINS_DIR, "load")

# AYON metadata keys
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

        pyblish.api.register_plugin_path(PUBLISH_PATH)
        register_loader_plugin_path(LOAD_PATH)

        # log.info("Installing callbacks ... ")
        # self._register_callbacks()

        log.info("Installing menu ... ")
        # need to figure out some other ways to deploy the menu

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
        return os.environ["AYON_CURRENT_WORKFILE"]

    def get_containers(self):
        return []

    def update_context_data(self, data, changes):
        ayon_metadata = get_ayon_metadata()
        context_data = ayon_metadata.get(AYON_CONTEXT_DATA, {})
        context_data.update(data)
        set_metadata(
            self.get_current_workfile(),
            AYON_CONTEXT_DATA,
            context_data
        )

    def get_context_data(self):
        metadata = get_ayon_metadata()
        return metadata.get(AYON_CONTEXT_DATA, {})


def imprint(filename, name, namespace, context, loader):
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

# get_instances
# set_instance,
# set_instances,
# remove_instance


def get_ayon_metadata():
    """get AYON relevant metadata from current file

    Returns:
        str : json string for meta data [key - value] list
    """
    host = registered_host()
    current_file = host.get_current_workfile()
    # need to convert string to dict
    metadata = utility_api.GetAPIMetaData(current_file)
    return json.loads(metadata)


def get_instances():
    """Retrieve all stored instances from the project settings."""
    ayon_metadata = get_ayon_metadata()
    return ayon_metadata[AYON_INSTANCES]


def ls():
    """List all AYON instances in the current file metadata."""
    ayon_metadata = get_ayon_metadata()
    return ayon_metadata.get(AYON_CONTAINERS, {})


def set_metadata(current_file: str, data_type: str, data: dict):
    """Set instance data into the current file metadata."""
    ayon_metadata = get_ayon_metadata()
    ayon_metadata[data_type] = data
    json_to_str_data = json.dumps(ayon_metadata)
    utility_api.SetAPIMetaData(current_file, json_to_str_data)

def set_instances(data, update=True):
    pass


def save_workfile(filepath=None):
    export_api.ExportZPrj(filepath)
    open_workfile(filepath)
    return filepath

def open_workfile(filepath):
    import_options = ApiTypes.ImportZPRJOption()
    import_api.importZprj(filepath, import_options)
    os.environ["AYON_CURRENT_WORKFILE"] = filepath