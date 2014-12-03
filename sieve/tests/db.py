import json

def get_db():
    return MockKVStore()




class MockKVStore(object):

    def __init__(self):
        self.db = {}
        self.index = {}


    def get(self, key):

        result = self.db.get(key)
        if result is None:
            return self.index.get(key)


    def set(self, key, value, uri=None, index=None,):

        self.db[key] = value
        if index is not None:
            self.index[index] = value
        if uri is not None:
            self.index[uri] = value


    def query(self, rules):

        found = []

        for key, item in self.db.iteritems():
            as_json = json.loads(item)
            ok = True
            for k, v in rules.iteritems():
                value = as_json.get(k)
                if value is None or value != v:
                    ok = False
            if ok:
                found.append(item)

        return found