import os
import unittest
from sieve.product_sieve import ProductSieve
from jsonschema import ValidationError


class TestValidSieve(unittest.TestCase):


    def test_valid_sieve(self):

        product_description = {"name": "My Table",
                   "description": "This is a very nice table",
                   "options":{
                       "color": ["red", "green", "blue"],
                       "size": ["big", "small"],
                   }
        }

        ProductSieve(product_description)


        # missing title
        product_description = {"description": "This is a very nice table",
                   "options":{
                       "color": ["red", "green", "blue"],
                       "size": ["big", "small"],
                   }
        }

        self.assertRaises(ValidationError, ProductSieve, product_description)


        # missing description
        product_description = {"name": "My Table",
                   "options":{
                       "color": ["red", "green", "blue"],
                       "size": ["big", "small"],
                   }
        }

        self.assertRaises(ValidationError, ProductSieve, product_description)


        # missing description
        product_description = {
            "name": "My Table",
            "description": "This is a very nice table",

        }

        ProductSieve(product_description)

    def test_valid_sieve_with_choice(self):

        product_description = {"name": "My Table",
                   "description": "This is a very nice table",
                   "options":{
                       "color": ["red", "green", "blue"],
                       "size": ["big", "small"],
                   }
        }

        ProductSieve(product_description)


    def test_dependencies(self):

        product_description =  {"name": "My Table",
                                "description": "This is a very nice table",
                                "options":{
                                    "color": ["red", "green", "blue"],
                                    "size": ["big", "small"],
                                    "wheels": ["none", "front", "back", "both"],
                                },
                                "dependencies": {
                                    "wheels": {
                                        "size": "big",
                                        "colour": ["red", "green"]
                                    }
                                }
                            }

        ProductSieve(product_description)





"""
Test to write

Validates => bool
against a global schema

Allows => bool
The child docoument meets the rules of the parent

Merge # src1, src2 => output
A union of all keys
An intersection of values

Extract
Pull out a subset by key

Match query a document set to find matching
A query that finds those that meet the rules

Patch
A union of all keys
Src keys overwrite dst


References

expand_refs
strip_refs


"""