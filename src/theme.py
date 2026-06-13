"""Constantes de design partagées par les widgets (voir README pour la palette).

Les couleurs sont exposées comme des listes RGBA mutables (`ACCENT`,
`ACCENT_DIM`, `TEXT`, `TEXT_DIM`, `BACKGROUND`, `EDIT`, `EDIT_DIM`). Les widgets
les utilisent soit via `from theme import ACCENT`, soit via `theme.ACCENT`
dans leurs règles kv.

Pour changer de thème (avant de construire l'interface), utiliser
`set_theme()` :

    import theme
    theme.set_theme(theme.LIGHT)

`set_theme()` met à jour ces listes *en place*, si bien que les références
déjà importées (`from theme import ACCENT`) restent valides et reflètent le
nouveau thème.
"""

from collections import namedtuple

__all__ = [
    'ACCENT', 'ACCENT_DIM', 'TEXT', 'TEXT_DIM', 'BACKGROUND', 'EDIT', 'EDIT_DIM',
    'Theme', 'DARK', 'LIGHT', 'THEMES', 'set_theme', 'get_theme',
]

Theme = namedtuple('Theme', [
    'ACCENT', 'ACCENT_DIM', 'TEXT', 'TEXT_DIM', 'BACKGROUND', 'EDIT', 'EDIT_DIM',
])

DARK = Theme(
    ACCENT=[0.2, 0.6, 0.8, 1],
    ACCENT_DIM=[0.2, 0.6, 0.8, 0.3],
    TEXT=[1, 1, 1, 1],
    TEXT_DIM=[1, 1, 1, 0.3],
    BACKGROUND=[0, 0, 0, 1],
    EDIT=[1, 0.5, 0, 1],
    EDIT_DIM=[1, 0.5, 0, 0.3],
)

LIGHT = Theme(
    ACCENT=[0.2, 0.6, 0.8, 1],
    ACCENT_DIM=[0.2, 0.6, 0.8, 0.3],
    TEXT=[0, 0, 0, 1],
    TEXT_DIM=[0, 0, 0, 0.3],
    BACKGROUND=[1, 1, 1, 1],
    EDIT=[1, 0.5, 0, 1],
    EDIT_DIM=[1, 0.5, 0, 0.3],
)

THEMES = {'dark': DARK, 'light': LIGHT}

# Listes mutables exposant le thème actif (par défaut : DARK)
ACCENT = list(DARK.ACCENT)
ACCENT_DIM = list(DARK.ACCENT_DIM)
TEXT = list(DARK.TEXT)
TEXT_DIM = list(DARK.TEXT_DIM)
BACKGROUND = list(DARK.BACKGROUND)
EDIT = list(DARK.EDIT)
EDIT_DIM = list(DARK.EDIT_DIM)

_active = DARK


def set_theme(theme):
    """Applique un thème (instance `Theme` ou nom dans `THEMES`).

    Met à jour les listes `ACCENT`, `ACCENT_DIM`, etc. en place : les
    références déjà importées (`from theme import ACCENT`) voient le
    nouveau thème. À appeler avant de construire l'interface.
    """
    global _active
    if isinstance(theme, str):
        theme = THEMES[theme]
    ACCENT[:] = theme.ACCENT
    ACCENT_DIM[:] = theme.ACCENT_DIM
    TEXT[:] = theme.TEXT
    TEXT_DIM[:] = theme.TEXT_DIM
    BACKGROUND[:] = theme.BACKGROUND
    EDIT[:] = theme.EDIT
    EDIT_DIM[:] = theme.EDIT_DIM
    _active = theme


def get_theme():
    """Renvoie le thème actif (instance `Theme`)."""
    return _active
