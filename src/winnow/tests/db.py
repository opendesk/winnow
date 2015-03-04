import json
from winnow.utils import json_loads, json_dumps

def get_db():
    return MockKVStore()




class MockKVStore(object):

    def __init__(self):
        self.db = {}
        self.fileset_index = {}


    def index_fileset(self, product_path, fileset_id):
        product_list = self.fileset_index.get(product_path)
        if product_list is None:
            self.fileset_index[product_path] = product_list = []
        product_list.append(fileset_id)

    def fileset_ids_for_product_path(self, product_path):
        return self.fileset_index.get(product_path)

    def get(self, key):
        # print "getting", key
        result = self.db.get(key)
        if result is None:
            return None
        return json_loads(result)


    def set(self, key, value):
        # print "setting", key, value

        v = json_dumps(value)
        self.db[key] = v

