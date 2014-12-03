import os
import json
from sieve import PublishedSieve
from product_exceptions import ProductExceptionFailedValidation, ProductExceptionLookupFailed, ProductExceptionNoAllowed



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
            "history_hash": {
                "type": "string"
            },
            "product_snapshot": {
                "type": "string"
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
            "quantity": {
                "type": "number"
            },
            "options": {},
        },
        "additionalProperties": False,
        "required": ["name", "product", "description"],
    }

    @classmethod
    def publish(self, db, fileset_json):
        from product_sieve import ProductSieve

        #ensure product ref is a snapshot
        fileset_json_dict = json.loads(fileset_json)
        product_json = db.get(fileset_json_dict[u"product"])
        if product_json is None:
            raise ProductExceptionLookupFailed("Couldn't find product %s in publish_fileset referred to by %s" % (self.product, self.doc))

        product = ProductSieve.from_json(product_json)
        if not product.is_snapshot:
            product = product.take_snapshot(db)
            product.save(db)

        fileset_json_dict[u"product"] = product.uri
        fileset = FilesetSieve.from_doc(json.dumps(fileset_json_dict))
        fileset.product = product.get_canonical_uri()

        if not product.allows(fileset):
            raise ProductExceptionNoAllowed

        fileset.save(db, index=fileset.get_canonical_uri())



    def uri_for_file_named(self, filename):
        product = self.product.split("@")[0]
        base, ext = os.path.splitext(product)
        parts = base.split("/")[1:4]
        path = "/".join(parts)

        base_uri = "%s/%s/%s" % (self.SIEVE_TYPE, path, self.name)
        return "%s/%s" % (base_uri, filename)


    def get_canonical_uri(self):
        return self.uri_for_file_named(self.name)


    def get_json(self):

        as_json = super(FilesetSieve, self).get_json()
        as_json[u"product"] = self.product;
        return as_json