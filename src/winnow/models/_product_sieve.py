from jsonschema import validate, ValidationError
import json
import time
from product_exceptions import ProductExceptionFailedValidation, ProductExceptionLookupFailed
from sieve.base_sieve import PublishedSieve
from _context_sieve import ContextSieve
from _fileset_sieve import FilesetSieve


import requests
import hashlib

"""

Product

"""




class ProductSieve(PublishedSieve):

    SIEVE_TYPE = u"product"

    SIEVE_SCHEMA = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "properties": {
            "range": {
                "type": "string"
            },
            "design": {
                "type": "string"
            },
            "name": {
                "type": "string"
            },
            "slug": {
                "type": "string"
            },
            "description": {
                "type": "string"
            },
            "quantity": {
                "type": "number"
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
            "public": {
                "type": "boolean"
            },
            "standard": {
                "type": "boolean"
            },
            "options": {},
        },
        "additionalProperties": False,
        "required": ["name", "slug", "description", "range", "design", "version"],
    }

    @classmethod
    def publish(cls, db, product_json):
        product = cls.from_doc(product_json)
        snapshot = product.take_snapshot(db)
        product.save(db, index=product.get_canonical_uri())
        return product


    def get_canonical_uri(self):
        return "%ss/%s/%s/%s" % (self.SIEVE_TYPE, self.range, self.design, self.slug)


    def merge_and_extract(self, db, context_uris, extractions=None):

        product = self

        if not product.is_snapshot():
            product = product.take_snapshot(db)
            product.save(db)

        for context_uri in context_uris:
            context_json = db.get(context_uri)
            if context_json is None:
                raise ProductExceptionLookupFailed("get_configuration_options: Couldn't find context %s" % context_uri)
            context = ContextSieve.from_json(context_json)
            product = product.merge(context)

        if extractions is None:
            return product
        else:
            return product.extract(extractions)


    def matching_filesets(self, db, context_uris):
        contextualised = self.merge_and_extract(db, context_uris)
        possible_filesets = self.all_canonical_filesets(db)
        return contextualised.match_intersects(possible_filesets)


    def all_canonical_filesets(self, db):
        return [FilesetSieve.from_json(j) for j in db.query({u"type": u"fileset", u"product": self.get_canonical_uri()})]