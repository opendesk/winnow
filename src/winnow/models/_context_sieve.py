from sieve.base_sieve import PublishedSieve

import os



class ContextSieve(PublishedSieve):

    SIEVE_TYPE = u"context"

    SIEVE_SCHEMA = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "properties": {
            "name": {
                "type": "string"
            },
            "slug": {
                "type": "string"
            },
            "description": {
                "type": "string"
            },
            "options": {},
        },
        "required": ["name", "slug", "description", "options"],

    }

    @classmethod
    def publish(self, db, context_json):
        context = ContextSieve.from_doc(context_json)
        context.save(db, index=context.get_canonical_uri())

    def get_canonical_uri(self):
        return "%s/%s" % (self.SIEVE_TYPE, self.slug)
