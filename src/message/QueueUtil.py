import importlib
import inspect

from message.Queue import Queue


def InstantiateQueue(queue_type_nama):
    module = importlib.import_module("message." + queue_type_nama)
    clsmembers = inspect.getmembers(module, inspect.isclass)
    for (_, c) in clsmembers:
        # check is proper plugin class
        if issubclass(c, Queue) & (c is not Queue):
            return c()

    return None
