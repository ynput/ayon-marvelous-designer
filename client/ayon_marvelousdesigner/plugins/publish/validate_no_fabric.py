"""Validate that workfile was saved before publishing."""
from typing import ClassVar

import fabric_api
import pyblish.api
from ayon_core.pipeline import PublishValidationError
from ayon_core.pipeline.publish import RepairAction


class ValidateNoFabric(pyblish.api.InstancePlugin):
    """Validate that workfile was saved."""

    order = pyblish.api.ValidatorOrder
    hosts: ClassVar = ["marvelousdesigner"]
    families: ClassVar = ["zfab"]
    label = "Validate No Fabric"
    actions: ClassVar = [RepairAction]

    def process(self, instance: pyblish.api.Instance) -> None:  # noqa: PLR6301
        """Process the instance to validate no fabric is selected.

        Args:
            instance (pyblish.api.Instance): The instance to validate.

        Raises:
            PublishValidationError: If a fabric is selected in the scene.
        """
        fabric_index = instance.data["fabricIndex"]
        fabric_name = instance.data["fabricName"]
        if fabric_api.GetFabricName(fabric_index) != fabric_name:
            msg = (
                f"Fabric '{fabric_name}' does not exist in the scene. "
                "Please reselect any fabric you want to publish "
                "and click 'Repair' action so that Ayon can reset for you."
            )
            raise PublishValidationError(
                msg
            )

    @classmethod
    def repair(cls, instance: pyblish.api.Instance) -> None:
        """Repair the instance by resetting the fabric index."""
        fabric_index = fabric_api.GetCurrentFabricIndex()
        instance.data["fabricIndex"] = fabric_index
        instance.data["fabricName"] = fabric_api.GetFabricName(fabric_index)
        cls.log.info(
            f"Reset fabric to '{instance.data['fabricName']}' "  # noqa: G004
            "in the instance data."
        )
