from jsonschema import validate
import json
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class ProductValidator(object):

    def __init__(self, meta_schema=None):

        if meta_schema is None:
            with open(os.path.join(THIS_DIR, "product_meta_schema.json")) as f:
                self.meta_schema = json.loads(f.read())
        else:
            self.meta_schema = meta_schema

        with open(os.path.join(THIS_DIR, "json-schema.org", "draft-04", "schema")) as f:
            core_meta_schema = json.loads(f.read())

        validate(self.meta_schema, core_meta_schema)




    def validate_as_opendesk_product(self, product_schema):

        validate(product_schema, self.meta_schema)