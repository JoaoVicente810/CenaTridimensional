"""Construção e animação dos elementos da cena."""

from .animation import update_animation
from .builder import make_scene

__all__ = ["make_scene", "update_animation"]
