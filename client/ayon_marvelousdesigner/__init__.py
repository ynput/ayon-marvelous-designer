"""Marvelous Designer integration package for AYON.

This package provides integration with Marvelous Designer,
including the addon class and host directory configuration.
"""
from .addon import (
    MARVELOUS_DESIGNER_HOST_DIR,
    MarvelousDesignerAddon,
)
from .version import __version__

__all__ = (
    "MARVELOUS_DESIGNER_HOST_DIR",
    "MarvelousDesignerAddon",
    "__version__"
)
