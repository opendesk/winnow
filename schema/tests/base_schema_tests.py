import os
import unittest
from schema.opendesk_schema import ProductValidator
from jsonschema import ValidationError, validate


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(THIS_DIR, "data")


TEST_PRODUCT_SCHEMA = {"$schema": "http://json-schema.org/draft-04/schema#",
    "description": "A Design for a table",
    "type": "object",
    "properties": {
        "configuration": {
            "type": "object",
            "properties":{
                "colour":{
                    "type": "string",
                    "enum": ["red", "green", "blue"]
                }
            },
            "required": [ "colour" ]
        }
    },
    "required": [ "configuration" ]
}


EXAMPLE_CONFIGURED_TABLE ={
    "configuration": {
        "colour": "red"
    }
}


class TestJsonSchemaValidator(unittest.TestCase):


    def test_can_validate_json(self):
        product = {"random": "json"}
        validator = ProductValidator(meta_schema={})
        validator.validate_as_opendesk_product(product)

    def test_for_invalid_meta_schema(self):
        schema = {"id": 42}
        self.assertRaises(ValidationError, ProductValidator, schema)

    def test_for_valid_meta_schema(self):
        validator = ProductValidator()





class TestJsonProductMetaSchema(unittest.TestCase):

    def setUp(self):
        self.validator = ProductValidator()

    def test_config(self):
        validate(EXAMPLE_CONFIGURED_TABLE, TEST_PRODUCT_SCHEMA)


    def test_top_of_schema(self):

        test_schema = {"title": "My Table Design",
            "description": "A Design for a very nice table",
            "type": "object",
            "properties": {
                "configuration": {
                    "type": "object",
                    "properties":{
                        "colour":{
                            "type": "string",
                            "enum": ["red", "green", "blue"]
                        }
                    }
                }
            },
            "required": [ "configuration" ]
        }

        self.validator.validate_as_opendesk_product(test_schema)



        #check for a title

        test_schema = {"description": "A Design for a very nice table",
            "type": "object",
            "properties": {
                "configuration": {
                    "type": "object",
                    "properties":{
                        "colour":{
                            "type": "string",
                            "enum": ["red", "green", "blue"]
                        }
                    }

                }
            },
            "required": [ "configuration" ]
        }

        self.assertRaises(ValidationError, self.validator.validate_as_opendesk_product, test_schema)

        #check for a description

        test_schema = {"title": "My Table Design",
            "type": "object",
            "properties": {
                "configuration": {
                    "type": "object",
                    "properties":{
                        "colour":{
                            "type": "string",
                            "enum": ["red", "green", "blue"]
                        }
                    }

                }
            },
            "required": [ "configuration" ]
        }

        self.assertRaises(ValidationError, self.validator.validate_as_opendesk_product, test_schema)

        test_schema = {"title": "My Table Design",
            "description": "A Design for a very nice table",
            "type": "object",
            "required": [ "configuration" ]
        }

        self.assertRaises(ValidationError, self.validator.validate_as_opendesk_product, test_schema)


def test_the_configuration(self):

        # wrong config type

        test_schema = {"title": "My Table Design",
            "description": "A Design for a very nice table",
            "type": "object",
            "properties": {
                "configuration": {
                    "type": "string",
                    "properties":{
                        "colour":{
                            "type": "string",
                            "enum": ["red", "green", "blue"]
                        }
                    }
                }
            },
            "required": [ "configuration" ]
        }

        self.assertRaises(ValidationError, self.validator.validate_as_opendesk_product, test_schema)


        test_schema = {"title": "My Table Design",
            "description": "A Design for a very nice table",
            "type": "object",
            "properties": {
                "configuration": {
                    "type": "object",
                    "properties":{
                        "colour":{
                            "type": "string",
                            "enum": ["red", "green", "blue"]
                        }
                    }
                }
            },
            "required": [ "configuration" ]
        }

        self.assertRaises(ValidationError, self.validator.validate_as_opendesk_product, test_schema)