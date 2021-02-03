from yaml import load, dump
import os

from config.Reader import Reader

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class Config:
    def __init__(self, config, name):
        path = self.get_configs_path(config, name)
        with open(path) as f:
            self._config = load(f, Loader=Loader)

    def get_configs_path(self, config, name):
        fill_path = os.path.realpath(__file__)
        path, _filename = os.path.split(fill_path)
        configs = os.path.realpath(path + ".." + os.path.sep + ".." +
                                   os.path.sep + ".." + os.path.sep + "configs" + os.path.sep + config + os.path.sep + name + ".yaml")
        return configs

    def __getattr__(self, name):
        if (name == "config"):
            return Reader(self._config)
