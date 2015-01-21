BASE = {
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
                "type": "object",
                "patternProperties": {
                    "[a-z]": {"oneOf": [{"type": "array"}, {"type": "string"}, {"type": "object"}, {"type": "number"}]},
                },
                "additionalProperties": False
            },
        },
        "required": ["name", "description", "options"],
    }

from winnow.models.product import SCHEMA as product