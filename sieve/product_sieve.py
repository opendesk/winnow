from jsonschema import validate

PRODUCT_SIEVE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "description": {
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
    "required": ["name", "description"],
    "definitions": {
        "simpleTypes": {
            "enum": [ "array", "boolean", "integer", "null", "number", "object", "string"]
        },
    },
}


class ProductSieve(object):

    def __init__(self, json):

        validate(json, PRODUCT_SIEVE_SCHEMA)
        self.json = json
        self.options = json.get("options")
        self.dependencies = json.get("dependencies")
        self.name = json["name"]
        self.description = json["description"]


    def check_dependencies(self):





