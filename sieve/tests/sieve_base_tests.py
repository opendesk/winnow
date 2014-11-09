import os
import unittest
from sieve.product_sieve import ProductSieve
from sieve.product_exceptions import ProductExceptionFailedValidation


class TestValidSieve(unittest.TestCase):


    def test_valid_sieve(self):

        product_description = {"name": "My Table",
                   "uri": "123",
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

        self.assertRaises(ProductExceptionFailedValidation, ProductSieve, product_description)

        # missing description
        product_description = {"name": "My Table",
                               "uri": "123",
                   "options":{
                       "color": ["red", "green", "blue"],
                       "size": ["big", "small"],
                   }
        }

        self.assertRaises(ProductExceptionFailedValidation, ProductSieve, product_description)

        # missing description
        product_description = {
            "name": "My Table",
            "uri": "123",
            "description": "This is a very nice table",

        }

        ProductSieve(product_description)


    def test_valid_sieve_with_choice(self):

        product_description = {"name": "My Table",
                    "uri": "123",
                   "description": "This is a very nice table",
                   "options":{
                       "color": ["red", "green", "blue"],
                       "size": ["big", "small"],
                   }
        }

        ProductSieve(product_description)


    def test_dependencies(self):

        product_description =  {"name": "My Table",
                                "uri": "123",
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


class TestSieveAllows(unittest.TestCase):


    def setUp(self):
        product_description = {"name": "My Table",
                    "uri": "123",
                   "description": "This is a very nice table",
                   "options":{
                       "color": ["red", "green", "blue"],
                       "size": ["big", "small"],
                   }
        }

        self.base_sieve = ProductSieve(product_description)


    def test_allows_subset(self):

        configured_product = {"name": "My Table",
                    "uri": "123",
                   "description": "This is a very nice table",
                   "options":{
                       "color": "red",
                       "size": "big",
                   }
        }

        configured_sieve = ProductSieve(configured_product)

        self.assertTrue(self.base_sieve.allows(configured_sieve))


    def test_allows_subset_without_a_key(self):

        configured_product = {"name": "My Table",
                    "uri": "123",
                   "description": "This is a very nice table",
                   "options":{
                       "color": "red",
                   }
        }

        configured_sieve = ProductSieve(configured_product)

        self.assertTrue(self.base_sieve.allows(configured_sieve))


    def test_allows_subset_without_an_extra_key(self):

        configured_product = {"name": "My Table",
                    "uri": "123",
                   "description": "This is a very nice table",
                   "options":{
                       "color": "red",
                       "age": "old",
                   }
        }

        configured_sieve = ProductSieve(configured_product)

        self.assertTrue(self.base_sieve.allows(configured_sieve))


    def test_allows_partial_config(self):

        configured_product = {"name": "My Table",
                    "uri": "123",
                   "description": "This is a very nice table",
                   "options":{
                       "color": ["red", "green", "blue"],
                       "age": "old",
                   }
        }

        configured_sieve = ProductSieve(configured_product)

        self.assertTrue(self.base_sieve.allows(configured_sieve))


    def test_allows_fails(self):

        configured_product = {"name": "My Table",
                    "uri": "123",
                   "description": "This is a very nice table",
                   "options":{
                       "color": ["red", "green"],
                       "size": "medium",
                   }
        }

        configured_sieve = ProductSieve(configured_product)

        self.assertFalse(self.base_sieve.allows(configured_sieve))


class TestSieveMerge(unittest.TestCase):


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


    def test_does_a_merge(self):

        some_constraints = {"name": "Some Constraints",
                    "uri": "567",
                   "description": "These are some things which are possible",
                   "options":{
                       "color": ["green", "blue", "orange"],
                       "size": ["big"],
                       "age": ["old", "young"]
                   }
        }

        constraints_sieve = ProductSieve(some_constraints)
        merged_sieve = self.base_sieve.merge(constraints_sieve)
        #self.assertTrue(iskindof(merged_sieve, ProductSieve))

        ## correct keys
        self.assertTrue(merged_sieve.keys == frozenset(["color", "material", "size", "age"]))

        ## name
        self.assertEqual(merged_sieve.name, "%s + %s" % (self.base_sieve.name, constraints_sieve.name))

        ## values
        self.assertEqual(merged_sieve.options["color"], frozenset(["green", "blue"]))
        self.assertEqual(merged_sieve.options["size"], frozenset(["big"]))
        self.assertEqual(merged_sieve.options["material"], frozenset(["metal", "wood", "paper"]))
        self.assertEqual(merged_sieve.options["age"], frozenset(["old", "young"]))


    def test_can_extract(self):

        extraction = self.base_sieve.extract(["color", "size"])
        self.assertTrue(extraction.keys == frozenset(["color", "size"]))
        self.assertEqual(extraction.options["color"], frozenset(["red", "green", "blue"]))
        self.assertEqual(extraction.options["size"], frozenset(["big", "small"]))


    def test_does_a_patch(self):

        a_child = {"name": "A Child",
                    "uri": "567",
                   "description": "New things I want",
                   "options":{
                       "color": ["green", "blue", "orange"],
                       "size": "big",
                       "age": ["old", "young"]
                   }
        }

        child_sieve = ProductSieve(a_child)

        patched_sieve = self.base_sieve.patch(child_sieve)

        ## correct keys
        self.assertTrue(patched_sieve.keys == frozenset(["color", "material", "size", "age"]))

        ## name
        self.assertEqual(patched_sieve.name, "%s ++ %s" % (self.base_sieve.name, child_sieve.name))

        ## values
        self.assertEqual(patched_sieve.options["color"], frozenset(["green", "blue", "orange"]))
        self.assertEqual(patched_sieve.options["size"], frozenset(["big"]))
        self.assertEqual(patched_sieve.options["material"], frozenset(["metal", "wood", "paper"]))
        self.assertEqual(patched_sieve.options["age"], frozenset(["old", "young"]))


    def test_match(self):

        configured_product_1 = {"name": "My Table",
                    "uri": "1",
                   "description": "This is a very nice table",
                   "options":{
                       "color": "red",
                       "size": "big",
                   }
        }


        configured_product_2 = {"name": "My Table",
                    "uri": "2",
                   "description": "This is a very nice table",
                   "options":{
                       "color": "red",
                   }
        }


        configured_product_3 = {"name": "My Table",
                    "uri": "3",
                   "description": "This is a very nice table",
                   "options":{
                       "color": "red",
                       "age": "old",
                   }
        }

        configured_product_4 = {"name": "My Table",
                    "uri": "123",
                   "description": "This is a very nice table",
                   "options":{
                       "color": ["red", "green"],
                       "size": "medium",
                   }
        }


        found = self.base_sieve.match([ProductSieve(configured_product_1),
                                       ProductSieve(configured_product_2),
                                       ProductSieve(configured_product_3),
                                       ProductSieve(configured_product_4)])


        self.assertEqual(len(found), 3)

"""
References
expand_refs
strip_refs
"""