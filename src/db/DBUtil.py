import importlib
import inspect

from db.DB import DB


def InstantiateDB(database_type):
    module = importlib.import_module("db." + database_type)
    clsmembers = inspect.getmembers(module, inspect.isclass)
    for (_, c) in clsmembers:
        # check is proper plugin class
        if issubclass(c, DB) & (c is not DB):
            return c()

    return None
