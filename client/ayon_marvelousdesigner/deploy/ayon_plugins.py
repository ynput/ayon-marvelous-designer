"""Deployed script with Ayon integration for Marvelous Designer.
 User needs to manually add this script into Marvelous Designer
Plugins -> Plug-in Managers.
"""  # noqa: D205

# -*- coding: utf-8 -*-
import os
import sys

# We need to add PYTHONPATH to sys.path to ensure Ayon modules are found
for path in os.environ["PYTHONPATH"].split(os.pathsep):
    if path and path not in sys.path:
        sys.path.append(path)


from ayon_core.pipeline import install_host
from ayon_marvelousdesigner.api import MarvelousDesignerHost


host = MarvelousDesignerHost()
install_host(host)
host.show_tools_dialog()
