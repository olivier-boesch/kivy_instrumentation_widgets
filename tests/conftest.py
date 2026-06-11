import os

# Doit être positionné avant tout import de Kivy : empêche Kivy d'interpréter
# les arguments de la ligne de commande de pytest.
os.environ.setdefault("KIVY_NO_ARGS", "1")
os.environ.setdefault("KIVY_NO_FILELOG", "1")

from kivy.clock import Clock  # noqa: E402


def pytest_runtest_teardown(item, nextitem):
    """Annule les évènements/animations programmés par le test précédent."""
    for event in list(Clock.get_events()):
        event.cancel()
