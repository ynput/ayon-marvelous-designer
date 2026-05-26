"""Pre-launch hook for Marvelous Designer workfile handling.

This module provides a hook that creates a temporary Zprj file for MD
when no last workfile exists or when not starting from the last workfile.
"""

import os
import shutil
from typing import ClassVar

from ayon_applications import LaunchTypes, PreLaunchHook
from ayon_core.pipeline import tempdir
from ayon_marvelousdesigner import MARVELOUS_DESIGNER_HOST_DIR


class CreateTempZprjFile(PreLaunchHook):
    """Create Temp Zprj File to Marvelous Designer.

    The temp zprj file would be created in Marvelous Designer prior to
    the launch of the software if there is no last workfile

    Hook `GlobalHostDataHook` must be executed before this hook.
    """
    app_groups: ClassVar = {"marvelousdesigner"}
    order = 12
    launch_types: ClassVar = {LaunchTypes.local}

    def execute(self) -> None:
        """Execute the pre-launch hook to create temp zprj file."""
        workfile_path = self.get_workfile_path()

        self.launch_context.launch_args.append(workfile_path)

    def get_workfile_path(self) -> str:
        workfile_path = self.data.get("workfile_path")
        if workfile_path:
            return workfile_path

        if self.data.get("start_last_workfile"):
            self.log.info("It is set to start last workfile on start.")
            last_workfile = self.data.get("last_workfile_path")
            if last_workfile and os.path.exists(last_workfile):
                return last_workfile

        source_template_file = os.path.join(
            MARVELOUS_DESIGNER_HOST_DIR, "default_zprj", "Untitled_MD.zprj"
        )
        staging_dir = tempdir.get_temp_dir(
            self.data["project_name"],
            use_local_temp=True
        )
        spm_filename = os.path.basename(source_template_file)
        workfile_path = os.path.join(staging_dir, spm_filename)
        shutil.copyfile(source_template_file, workfile_path)
        self.launch_context.env["AYON_TEMP_DIR"] = staging_dir
        return workfile_path
