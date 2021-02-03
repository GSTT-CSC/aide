from plugin.Types import PluginType

class Plugin:
    def __init__(self):
        self.description = 'UNKNOWN'
        self.type = PluginType.UNKNOWN

        self.data = lambda: None

    def process(self):
        """The method that we expect all plugins to implement. This is the
        method that our framework will call
        """
        raise NotImplementedError
