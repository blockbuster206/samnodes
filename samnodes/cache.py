import os
import json


class Cache:
    def __init__(self):
        if os.path.isfile("samnnodes.cache"):
            with open("samnnodes.cache", 'r') as cache:
                self.cache = json.load(cache)
                cache.close()
            return

        self.cache = {}

    def save_cache(self):
        with open("samnnodes.cache", 'rw') as cache:
            json.dump(self.cache, cache, indent=4)

    def add_entry(self, username, filepath, source_distributor):
        pass
