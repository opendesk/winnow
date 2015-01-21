import json
from winnow.utils import json_loads, json_dumps

def get_db():
    return MockKVStore()




class MockKVStore(object):

    def __init__(self):
        self.db = {}

    def get(self, key):
        result = self.db.get(key)
        if result is None:
            return None
        return json_loads(result)


    def set(self, key, value):
        v = json_dumps(value)
        self.db[key] = v

