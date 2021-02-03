import importlib
import inspect
import sys
import os
from plugin.Plugin import Plugin


class PluginManager:
    def __init__(self):
        # we are adding external scripts - this may be changed in final version to configured path
        plugins_path = os.path.join(__file__, "..", "..", "..", "scripts")
        plugins_path = os.path.abspath(plugins_path)
        if plugins_path not in sys.path:
            sys.path.append(plugins_path)

    def get(self, plugin_category, plugin_name):
        module = importlib.import_module(
            "plugins." + plugin_category + "." + plugin_name)
        clsmembers = inspect.getmembers(module, inspect.isclass)
        for (_, c) in clsmembers:
            # check is proper plugin class
            if issubclass(c, Plugin) & (c is not Plugin):
                return c()

        raise NameError("Plugin not exist: " +
                        plugin_category + "." + plugin_name)
