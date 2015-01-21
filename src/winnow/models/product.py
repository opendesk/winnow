
SCHEMA = {
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