import jsonschema
import os
import json

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "schemata")

reference_store = {}

def add_file(store, dir_name, names):
    for file_name in names:
        file_path = os.path.join(dir_name, file_name)
        if os.path.isfile(file_path):
            if file_path.endswith(".json"):
                with open(file_path, "r") as f:
                    schema = json.loads(f.read())
                    jsonschema.Draft4Validator.check_schema(schema)
                    store[schema["id"]] = schema

def validate(doc):
    type = doc.get("schema")
    if type is None:
        return


    schema = reference_store[type]
    resolver = jsonschema.RefResolver(type, schema, store=reference_store)
    validator = jsonschema.Draft4Validator(schema, resolver=resolver)
    validator.validate(doc)


os.path.walk(SCHEMA_DIR, add_file, reference_store)