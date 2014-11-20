import os
import json
from sieve import PublishedSieve
from product_sieve import ProductSieve
from product_exceptions import ProductExceptionFailedValidation, ProductExceptionLookupFailed, ProductExceptionNoAllowed



"""

Fileset

files []


"""




class FilesetSieve(PublishedSieve):

    SIEVE_TYPE = u"fileset"

    SIEVE_SCHEMA = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "properties": {
            "type": {
                "type": "string"
            },
            "uri": {
                "type": "string"
            },
            "name": {
                "type": "string"
            },
            "product": {
                "type": "string"
            },
            "product_frozen": {
                "type": "string"
            },
            "product_ancestors": {
                "type": "array"
            },
            "files": {
                "type": "array"
            },
            "description": {
                "type": "string"
            },
            "created": {
                "type": "string"
            },
            "history": {
                "type": "array"
            },
            "frozen_uri": {
                "type": "string"
            },
            "options": {},
        },
        "additionalProperties": False,
        "required": ["type", "uri", "name", "product", "description"],
    }


    def freeze_product(self, db):

        product_dict = db.get(self.product)

        if product_dict is None:
            raise ProductExceptionLookupFailed("Couldn't find product %s in publish_fileset referred to by %s" % (self.product, self.json_dict))

        product = ProductSieve(json.loads(product_dict))
        if not product.is_frozen:
            product = product.patch_upstream(db)
            product.save(db, overwrite=False)

        self.json_dict[u"product_frozen"] = product.frozen_uri
        self.json_dict[u"product_history"] = product.history

        return product


    def add_files(self, db, cad_files):

        files = []
        self.json_dict[u"files"] = files

        if cad_files is not None:
            for k, v in cad_files.iteritems():
                uri = self.uri_for_file_named(k)
                self.files.append(uri)
                db.set(uri, v)


    def uri_for_file_named(self, filename):
        base, ext = os.path.splitext(self.product)
        parts = base.split("/")[1:4]
        path = "/".join(parts)

        base_uri = "%s/%s/%s" % (self.SIEVE_TYPE, path, self.name)
        return "%s/%s" % (base_uri, filename)


    def get_uri(self):
        return self.uri_for_file_named(self.name)


    uri = property(get_uri)

