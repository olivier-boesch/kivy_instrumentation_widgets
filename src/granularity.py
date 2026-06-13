"""Utilitaires de quantification de valeurs partagés par les widgets.

La propriété `granularity` exposée par les widgets représente un pas de
quantification : la valeur est arrondie au multiple de `granularity` le plus
proche (ex. granularity=0.5 -> 2.5, 3.0 ; granularity=2 -> 4, 6, 8).
`granularity=None` désactive l'arrondi.
"""

_DEFAULT_DECIMALS = 2

__all__ = ['snap_value', 'decimals_for', 'format_value']


def decimals_for(granularity):
    """Nombre de décimales à afficher pour un pas `granularity`.

    Déduit du nombre de décimales de `granularity` lui-même.
    `granularity=None` renvoie `_DEFAULT_DECIMALS`.
    """
    if granularity is None:
        return _DEFAULT_DECIMALS
    text = repr(float(granularity))
    if '.' in text:
        return len(text.split('.')[1].rstrip('0'))
    return 0


def snap_value(magnitude, granularity):
    """Arrondit `magnitude` au multiple de `granularity` le plus proche.

    `granularity=None` (ou `0`) renvoie `magnitude` sans arrondi.
    """
    if not granularity:
        return magnitude
    snapped = round(magnitude / granularity) * granularity
    return round(snapped, decimals_for(granularity))


def format_value(magnitude, granularity):
    """Formate `magnitude` avec le nombre de décimales adapté à `granularity`."""
    return f"{magnitude:.{decimals_for(granularity)}f}"
