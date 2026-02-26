"""Creator plugin for creating workfiles."""
from ayon_core.pipeline import AutoCreator, CreatedInstance
from ayon_marvelousdesigner.api.pipeline import (
    get_instances_values,
    set_instance,
    set_instances,
)


class CreateWorkfile(AutoCreator):
    """Workfile auto-creator."""
    identifier = "io.ayon.creators.marvelousdesigner.workfile"
    label = "Workfile"
    product_base_type = "workfile"
    product_type = product_base_type
    icon = "document"

    default_variant = "Main"
    settings_category = "marvelousdesigner"

    def create(self) -> None:
        """Create or update the workfile instance in the current context."""
        variant = self.default_variant
        project_name = self.project_name
        folder_path = self.create_context.get_current_folder_path()
        task_name = self.create_context.get_current_task_name()
        host_name = self.create_context.host_name

        # Workfile instance should always exist and must only exist once.
        # As such we'll first check if it already exists and is collected.
        current_instance = next(
            (
                instance for instance in self.create_context.instances
                if instance.creator_identifier == self.identifier
            ), None)

        project_entity = self.create_context.get_current_project_entity()
        folder_entity = self.create_context.get_current_folder_entity()
        task_entity = self.create_context.get_current_task_entity()

        project_name = project_entity["name"]
        folder_path = folder_entity["path"]
        task_name = task_entity["name"]
        host_name = self.create_context.host_name

        current_folder_path = None
        if current_instance is not None:
            current_folder_path = current_instance["folderPath"]

        if current_instance is None:
            self.log.info("Auto-creating workfile instance...")
            product_name = self.get_product_name(
                project_name=project_name,
                project_entity=project_entity,
                folder_entity=folder_entity,
                task_entity=task_entity,
                variant=variant,
                host_name=host_name,
                product_type=self.product_base_type,
            )
            data = {
                "folderPath": folder_path,
                "task": task_name,
                "variant": variant
            }
            current_instance = self.create_instance_in_context(product_name,
                                                               data)
        elif (
            current_folder_path != folder_path
            or current_instance["task"] != task_name
        ):
            # Update instance context if is not the same
            product_name = self.get_product_name(
                project_name=project_name,
                project_entity=folder_entity,
                folder_entity=folder_entity,
                task_entity=task_entity,
                variant=variant,
                host_name=host_name,
                product_type=self.product_base_type,
            )
            current_instance["folderPath"] = folder_path
            current_instance["task"] = task_name
            current_instance["productName"] = product_name
        set_instance(
            instance_id=current_instance.get("instance_id"),
            instance_data=current_instance.data_to_store()
        )

    def collect_instances(self) -> None:
        """Collect existing instances from MD and add them to the context."""
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

    def create_instance_in_context(
            self, product_name: str, data: dict) -> CreatedInstance:
        """Create a new instance in the current context.

        Args:
            product_name (str): The name of the product to create.
            data (dict): The data for the instance.

        Returns:
            CreatedInstance: The newly created instance.
        """
        instance = CreatedInstance(
            product_base_type=self.product_base_type,
            product_type=self.product_base_type,
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
            data (dict): The existing instance data.

        Returns:
            CreatedInstance: The created instance from existing data.
        """
        instance = CreatedInstance.from_existing(data, self)
        self.create_context.creator_adds_instance(instance)
        return instance
