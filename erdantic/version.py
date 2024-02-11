import importlib_metadata

__version__ = importlib_metadata.version(__name__.split(".", 1)[0])
