

def get_db():
    return MockKVStore()




class MockKVStore(object):

    def __init__(self):
        self.db = {}


    def get(self, key):

        return self.db.get(key)


    def set(self, key, value, overwrite=True):

        if not overwrite:
            existing = self.db.get(key)
            if existing is not None:
                return

        self.db[key] = value