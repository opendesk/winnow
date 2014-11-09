import os
import unittest
from sieve.product_sieve import ProductSieve
from jsonschema import ValidationError

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(THIS_DIR, "data")

class TestSieveRefs(unittest.TestCase):


    def setUp(self):
        product_description = {"name": "My Table",
                   "uri": "123",
                   "description": "This is a very nice table",
                   "options":{
                       "color": ["red", "green", "blue"],
                       "size": ["big", "small"],
                       "material": ["metal", "wood", "paper"],
                   }
        }

        self.base_sieve = ProductSieve(product_description)





"""
References
expand_refs
strip_refs
"""