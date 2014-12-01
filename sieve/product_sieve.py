from jsonschema import validate, ValidationError
import json
import time
from product_exceptions import ProductExceptionFailedValidation, ProductExceptionLookupFailed
from sieve import PublishedSieve
from context_sieve import ContextSieve


import requests
import hashlib

"""

Product

name: Is a meaningful name which identifies an individual product
design: Is a familly of products

design and name are used to create a unique uri in the OpenDesk namespace

upstream is the url of a product from which this product inherits.
This may be a uri in the OpenDesk namespace like this: design_name/product_name
Or it may be an http or git reference

Such a reference reffers to the head version of this model unless the reference is qualified with a git object ref

design_name/product_name@1234567890


"""




class ProductSieve(PublishedSieve):

    SIEVE_TYPE = "product"

    SIEVE_SCHEMA = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "properties": {
            "type": {
                "type": "string"
            },
            "range": {
                "type": "string"
            },
            "created": {
                "type": "string"
            },
            "design": {
                "type": "string"
            },
            "name": {
                "type": "string"
            },
            "description": {
                "type": "string"
            },
            "quantity": {
                "type": "number"
            },
            "uri": {
                "type": "string"
            },
            "frozen_uri": {
                "type": "string"
            },
            "version": {
                "type": "array",
                "items": {
                    "type": "number"
                },
            },
            "src_url": {
                "type": "string"
            },
            "upstream": {
                "type": "string"
            },
            "history": {
                "type": "array"
            },
            "options": {},
        },
        "additionalProperties": False,
        "required": ["uri", "name", "description", "type", "range", "design", "version"],
    }


    def get_uri(self):
        return "%s/%s/%s/%s" % (self.SIEVE_TYPE, self.range, self.design, self.name)


    def get_version_uri(self):
        version = self.version
        return u"%s@xxxxxxxx::%s::%s::%s" % (self.uri, version[0], version[1], version[2])


    def merge_and_extract(db, product, context_uris, extractions=None):

        for context_uri in context_uris:
            context_json = db.get(context_uri)
            if context_json is None:
                raise ProductExceptionLookupFailed("get_configuration_options: Couldn't find context %s" % context_uri)
            context = ContextSieve.from_json(context_json)
            if not product.is_frozen:
                    product = product.patch_upstream(db)
                    product.save(db, overwrite=False)
            product = product.merge(context)

        if extractions is None:
            return product
        else:
            return product.extract(extractions)


