import os
from ayon_core.addon import AYONAddon, IHostAddon

from .version import __version__


MARVELOUS_DESIGNER_HOST_DIR = os.path.dirname(os.path.abspath(__file__))


class MarvelousDesignerAddon(AYONAddon, IHostAddon):
    name = "marvelousdesigner"
    version = __version__
    host_name = "marvelousdesigner"

    def add_implementation_envs(self, env, _app):
        env.pop("QT_AUTO_SCREEN_SCALE_FACTOR", None)

    def get_launch_hook_paths(self, app):
        if app.host_name != self.host_name:
            return []
        return [
            os.path.join(MARVELOUS_DESIGNER_HOST_DIR, "hooks")
        ]

    def get_workfile_extensions(self):
        return [".zprj"]
