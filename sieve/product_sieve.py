from jsonschema import validate, ValidationError
import json
import time
from product_exceptions import ProductExceptionFailedValidation, ProductExceptionLookupFailed
from sieve import Sieve

import requests






class ProductSieve(Sieve):

    SIEVE_SCHEMA = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "properties": {
            "name": {
                "type": "string"
            },
            "design": {
                "type": "string"
            },
            "description": {
                "type": "string"
            },
            "src_url": {
                "type": "string"
            },
            "options": {
                "patternProperties": {
                    "[a-z]": {"oneOf": [{"type": "array"}, {"type": "string"}, {"type": "object"}, {"type": "number"}]},
                },
                "additionalProperties": False
            },
            "dependencies": {
                "[a-z]": {"type": "object"},
            }
        },
        "required": ["name", "description", "uri"],
        "definitions": {
            "simpleTypes": {
                "enum": [ "array", "boolean", "integer", "null", "number", "object", "string"]
            },
        },
    }


    def __init__(self, json_dict, src_url=None):

        if src_url is not None:
            json_dict["src_url"] = src_url
        super(ProductSieve, self).__init__(json_dict)


    def with_expanded_ancestors(self, db):
        if self.upstream is None:
            return self
        else:
            upstream_dict = db.get(self.upstream)
            if upstream_dict is None:
                try:
                    rsp = requests.get(self.upstream)
                    if rsp.status_code < 300:
                        upstream_dict = rsp.json()
                    else:
                        raise ProductExceptionLookupFailed("Couldn't find the upstream model")
                except Exception, e:
                    raise ProductExceptionLookupFailed(e)

            upstream_product = ProductSieve(upstream_dict)
            self.expanded_ancestors(upstream_product)
            return upstream_product.patch(self)


    def get_uri(self):
        return "product/%s/%s.json" % (self.design, self.name)

    uri = property(get_uri)
