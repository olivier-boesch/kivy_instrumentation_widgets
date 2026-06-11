"""Utilitaires de rendu canvas partagés par les widgets."""

from kivy.core.text import Label as CoreLabel


def make_texture(text, font_size, color, **kwargs):
    """Crée et rafraîchit un CoreLabel, puis renvoie sa texture."""
    lbl = CoreLabel(text=text, font_size=font_size, color=color, **kwargs)
    lbl.refresh()
    return lbl.texture
