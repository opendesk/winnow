from sieve import PublishedSieve

import os



class ContextSieve(PublishedSieve):

    SIEVE_TYPE = u"context"

    SIEVE_SCHEMA = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "properties": {
            "type": {
                "type": "string"
            },
            "name": {
                "type": "string"
            },
            "description": {
                "type": "string"
            },
            "options": {},
        },
        "required": ["type", "name", "description"],

    }


    def get_uri(self):
        return "%s/%s" % (self.SIEVE_TYPE, self.name)


    uri = property(get_uri)

