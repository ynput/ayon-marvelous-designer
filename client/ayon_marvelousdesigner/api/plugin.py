"""Creator plugin for Marvelous Designer."""
from ayon_core.pipeline import CreatedInstance, Creator

from ayon_marvelousdesigner.api.pipeline import (
    get_instances_values,
    remove_instance,
    set_instance,
    set_instances,
)


class MDCreator(Creator):
    """Marvelous Designer Creator."""
    settings_category = "marvelousdesigner"

    def create(
            self, product_name: str,
            instance_data: dict, pre_create_data: dict
        ) -> None:
        """Create a new instance in the current context."""
        instance = self.create_instance_in_context(product_name,
                                                   instance_data)
        set_instance(
            instance_id=instance["instance_id"],
            instance_data=instance.data_to_store()
        )

    def collect_instances(self) -> None:
        """Collect existing instances from MD and add them to the context.

        This method retrieves instances that match the current creator's
        identifier or product type and creates context instances from the
        existing data.
        """
        for instance in get_instances_values():
            if (
                instance.get("creator_identifier") == self.identifier
                # Backwards compatibility
                or instance.get("productType") == self.product_base_type
            ):
                self.create_instance_in_context_from_existing(instance)

    def update_instances(self, update_list: list) -> None:  # noqa: PLR6301
        """Update existing instances with new data."""
        instance_data_by_id = {}
        for instance, _changes in update_list:
            # Persist the data
            instance_id = instance.get("instance_id")
            instance_data = instance.data_to_store()
            instance_data_by_id[instance_id] = instance_data
        set_instances(instance_data_by_id, update=True)

    def remove_instances(self, instances: list) -> None:
        """Remove instances from MD and the current context."""
        for instance in instances:
            remove_instance(instance["instance_id"])
            self._remove_instance_from_context(instance)

    # Helper methods (this might get moved into Creator class)
    def create_instance_in_context(
            self, product_name: str, data: dict) -> CreatedInstance:
        """Create a new instance in the current context.

        Args:
            product_name (str): Name of the product.
            data (dict): Data associated with the instance.

        Returns:
            CreatedInstance: The created instance.
        """
        product_type = data.get("productType")
        if not product_type:
            product_type = self.product_base_type
        instance = CreatedInstance(
            product_base_type=self.product_base_type,
            product_type=product_type,
            product_name=product_name,
            data=data,
            creator=self
        )
        self.create_context.creator_adds_instance(instance)
        return instance

    def create_instance_in_context_from_existing(
            self, data: dict) -> CreatedInstance:
        """Create an instance in the current context from existing data.

        Args:
            data (dict): Existing instance data.

        Returns:
            CreatedInstance: The created instance.
        """
        instance = CreatedInstance.from_existing(data, self)
        self.create_context.creator_adds_instance(instance)
        return instance
