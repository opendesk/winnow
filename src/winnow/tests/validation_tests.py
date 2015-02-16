import os
import json
import unittest
import winnow


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

class TestValidSieve(unittest.TestCase):


    def test_validate_product(self):

        with open(os.path.join(DATA_DIR, "product.json"), "r") as f:
            product_dict = json.loads(f.read())
        winnow.validate(product_dict)


    def test_validate_product_with_numeric(self):

        with open(os.path.join(DATA_DIR, "product_with_thickness.json"), "r") as f:
            product_dict = json.loads(f.read())
        winnow.validate(product_dict)


    def test_validate_product_with_numeric_fail(self):

        with open(os.path.join(DATA_DIR, "product_with_thickness_broken.json"), "r") as f:
            product_dict = json.loads(f.read())
        self.assertRaises(Exception, winnow.validate, product_dict)



    def test_validate_fileset(self):
        with open(os.path.join(DATA_DIR, "fileset.json"), "r") as f:
            fileset_dict = json.loads(f.read())

        winnow.validate(fileset_dict)