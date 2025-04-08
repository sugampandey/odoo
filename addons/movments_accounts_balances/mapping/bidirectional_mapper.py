from collections import ChainMap

class BidirectionalMapper:
    def __init__(self, mapping):
        self._forward = mapping
        self._reverse = {v: k for k, v in mapping.items()}
        self.lookup = ChainMap(self._forward, self._reverse)

    def get(self, key):
        return self.lookup.get(key)
