

def get_db():
    return MockKVStore()




class MockKVStore(object):

    def __init__(self):
        self.db = {}




    def get(self, key):

        return self.db.get(key)


    def set(self, key, value):

        self.db[key] = value