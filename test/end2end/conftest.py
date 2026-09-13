"""Isolate OVOS caches before test modules import the runtime."""
from thalovant_skillkit.testing_ovos import isolated_xdg


def pytest_configure(config):
    isolation = isolated_xdg()
    isolation.__enter__()
    config.add_cleanup(lambda: isolation.__exit__(None, None, None))
