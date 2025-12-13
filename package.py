# Required: lower case addon name e.g. 'deadline', otherwise addon
#   will be invalid
name = "marvelous_designer"

# Optional: Addon title shown in UI, 'name' is used by default e.g. 'Deadline'
title = "Marvelous Designer"

# Required: Valid semantic version (https://semver.org/)
version = "0.1.0"

# Name of client code directory imported in AYON launcher
app_host_name = "marvelousdesigner"
# - do not specify if there is no client code

client_dir = "ayon_marvelousdesigner"
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
ayon_compatible_addons = {}
