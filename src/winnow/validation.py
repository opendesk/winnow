import jsonschema
import os
import json

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "schemata")

OPTIONS_SCHEMA_FILEPATH = os.path.join(SCHEMA_DIR, "options.json")
VALUE_SCHEMA_FILEPATH = os.path.join(SCHEMA_DIR, "value.json")
PRODUCT_SCHEMA_FILEPATH = os.path.join(SCHEMA_DIR, "product.json")
FILESET_SCHEMA_FILEPATH = os.path.join(SCHEMA_DIR, "fileset.json")
TYPED_SCHEMA_FILEPATH = os.path.join(SCHEMA_DIR, "typed.json")

def schema_for_path(path):
    with open(path, "r") as f:
        schema = json.loads(f.read())
        jsonschema.Draft4Validator.check_schema(schema)
        return schema

reference_store = {
    u"http://opendesk.cc/schemata/product.json": schema_for_path(PRODUCT_SCHEMA_FILEPATH),
    u"http://opendesk.cc/schemata/value.json": schema_for_path(VALUE_SCHEMA_FILEPATH),
    u"http://opendesk.cc/schemata/options.json": schema_for_path(OPTIONS_SCHEMA_FILEPATH),
    u"http://opendesk.cc/schemata/typed.json": schema_for_path(TYPED_SCHEMA_FILEPATH),
    u"http://opendesk.cc/schemata/fileset.json": schema_for_path(FILESET_SCHEMA_FILEPATH),
}

def validate(doc):
    type = doc.get("schema")
    if type is None:
        type = "http://opendesk.cc/schemata/options.json"
    schema = reference_store[type]
    resolver = jsonschema.RefResolver("http://opendesk.cc/schemata/product.json", schema, store=reference_store)
    validator = jsonschema.Draft4Validator(schema, resolver=resolver)
    validator.validate(doc)