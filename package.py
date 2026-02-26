name = "marvelous_designer"
title = "Marvelous Designer"
version = "1.0.2"

client_dir = "ayon_marvelousdesigner"
app_host_name = "marvelousdesigner"

project_can_override_addon_version = True

# Version compatibility with AYON server
# ayon_server_version = ">=1.0.7"
# Version compatibility with AYON launcher
# ayon_launcher_version = ">=1.0.2"

# Mapping of addon name to version requirements
# - addon with specified version range must exist to be able to use this addon
ayon_required_addons = {}
# Mapping of addon name to version requirements
# - if addon is used in the same bundle, the version range must be valid
ayon_compatible_addons = {
    "core": ">=1.7.2",
}
