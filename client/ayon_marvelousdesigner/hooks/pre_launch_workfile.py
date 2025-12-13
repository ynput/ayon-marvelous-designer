import os
import shutil
from ayon_applications import PreLaunchHook, LaunchTypes
from ayon_core.pipeline import tempdir
from ayon_marvelousdesigner import MARVELOUS_DESIGNER_HOST_DIR


class CreateTempZprjFile(PreLaunchHook):
    """Create Temp Zprj File to Marvelous Designer.

    The temp zprj file would be created in Marvelous Designer prior to
    the launch of the software if there is no last workfile

    Hook `GlobalHostDataHook` must be executed before this hook.
    """
    app_groups = {"marvelousdesigner"}
    order = 12
    launch_types = {LaunchTypes.local}

    def execute(self):
        last_workfile = self.data.get("last_workfile_path")
        if self.data.get("start_last_workfile")  \
            and last_workfile  \
                and os.path.exists(last_workfile):
            self.log.info("It is set to start last workfile on start.")
        else:
            source_template_file = os.path.join(
                MARVELOUS_DESIGNER_HOST_DIR, "default_zprj", "Default_MD.zprj"
            )
            staging_dir = tempdir.get_temp_dir(
                self.data["project_name"],
                use_local_temp=True
            )
            spm_filename = os.path.basename(source_template_file)
            last_workfile = os.path.join(staging_dir, spm_filename)
            shutil.copyfile(source_template_file, last_workfile)

        self.launch_context.launch_args.append(last_workfile)

        self.launch_context.env["AYON_CURRENT_WORKFILE"] = last_workfile
