class Reader:
    def __init__(self, dict):
        self.dict = dict

    def __getattr__(self, name):
        if isinstance(self.dict[name], dict):
            return Reader(self.dict[name])
        return self.dict[name]
