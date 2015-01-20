import unittest
from sieve.product.base_sieve import Sieve, json_dumps, json_loads
from sieve.product.base import WinnowVersion
from copy import deepcopy
from sieve.options_exceptions import OptionsExceptionFailedValidation, OptionsExceptionNoAllowed
import sieve.options_operations as winnow

from decimal import Decimal


from db import MockKVStore


BASE_PRODUCT =  {u"name": u"table",
                    u"description": u"This is a very nice table",
                    u"options":{
                        u"color": [u"red", u"green", u"blue"],
                        u"size": [u"big", u"small"],
                        u"tool": [u"cnc", u"laser"],
                        u"material": [u"wood", u"metal", u"plastic"]
                    }
                }


class TestValidSieve(unittest.TestCase):

    def setUp(self):
        self.db = MockKVStore()


    def test_valid_sieve(self):

        version = WinnowVersion.create(self.db, BASE_PRODUCT, {})

        broken_option = deepcopy(BASE_PRODUCT)
        broken_option[u"options"] = u"text"

        self.assertRaises(OptionsExceptionFailedValidation, Sieve, broken_option)



class TestSieveAllows(unittest.TestCase):


    def setUp(self):
        self.db = MockKVStore()
        self.base_version = WinnowVersion.create(self.db, BASE_PRODUCT, {})


    def test_allows_subset(self):

        configured_option = deepcopy(BASE_PRODUCT)
        configured_option[u"options"][u"color"] = u"red"

        configured_version = WinnowVersion.create(self.db, configured_option, {})

        self.assertTrue(winnow.allows(self.base_version, configured_version))


        # configured_option = deepcopy(BASE_PRODUCT)
        # configured_option[u"options"][u"color"] = [u"red", u"green"]
        # configured_sieve = Sieve(configured_option)
        #
        # self.assertTrue(self.base_sieve.allows(configured_sieve))
        #
        # configured_option = deepcopy(BASE_PRODUCT)
        # configured_option[u"options"][u"color"] = [u"red", u"green"]
        # configured_option[u"options"][u"tool"] = [u"cnc"]
        # configured_sieve = Sieve(configured_option)
        #
        # self.assertTrue(self.base_sieve.allows(configured_sieve))
#
#
#     def test_allows_subset_without_a_key(self):
#
#         configured_option = deepcopy(BASE_PRODUCT)
#         del configured_option[u"options"][u"color"]
#         configured_sieve = Sieve(configured_option)
#         self.assertTrue(self.base_sieve.allows(configured_sieve))
#
#
#     def test_allows_subset_with_an_extra_key(self):
#
#         configured_option = deepcopy(BASE_PRODUCT)
#         configured_option[u"options"][u"wheels"] = [u"big", u"small"]
#         configured_sieve = Sieve(configured_option)
#         self.assertTrue(self.base_sieve.allows(configured_sieve))
#
#
#     def test_allows_fails(self):
#
#         configured_option = deepcopy(BASE_PRODUCT)
#         configured_option[u"options"][u"color"] = u"purple"
#         configured_sieve = Sieve(configured_option)
#         self.assertFalse(self.base_sieve.allows(configured_sieve))
#
#
# class TestSieveMerge(unittest.TestCase):
#
#
#     def setUp(self):
#         self.base_sieve = Sieve(BASE_PRODUCT)
#
#     def test_does_a_merge(self):
#
#         other_dict =  {u"name": u"something",
#                         u"description": u"these are other options",
#                         u"options":{
#                             u"color": [u"red", u"blue"],
#                             u"size": [u"big", u"medium", u"small"],
#                             u"tool": [u"cnc", u"laser", u"plaster"],
#                             u"days": [u"tuesday", u"thursday"],
#                             u"drinks": [u"beer", u"coffee"],
#                             u"snacks": [u"crisps", u"cheese", u"apple"]
#                         }
#                     }
#
#         expected =  {u"name": u"table",
#                     u"description": u"This is a very nice table",
#                     u"options":{
#                         u"color": [u"blue", u"red"],
#                         u"size": [u"big", u"small"],
#                         u"tool": [u"cnc", u"laser"],
#                         u"material": [u"wood", u"metal", u"plastic"],
#                         u"days": [u"tuesday", u"thursday"],
#                         u"drinks": [u"beer", u"coffee"],
#                         u"snacks": [u"crisps", u"cheese", u"apple"]
#                     }
#                 }
#
#         other_sieve = Sieve(other_dict)
#         merged = self.base_sieve.merge(other_sieve)
#         self.maxDiff = None
#         self.assertEqual(merged.doc, expected)
#
#
#
#
# class TestSieveExtract(unittest.TestCase):
#
#     def setUp(self):
#         self.base_sieve = Sieve(BASE_PRODUCT)
#
#
#     def test_can_extract(self):
#
#         expected =  {u"name": u"table",
#                     u"description": u"This is a very nice table",
#                     u"options":{
#                         u"color": [u"red", u"green", u"blue"],
#                         u"size": [u"big", u"small"]
#                     }
#                 }
#
#         extracted = self.base_sieve.extract([u"color", u"size"])
#         self.maxDiff = None
#         self.assertEqual(extracted.get_json(), expected)
#
#
#
#
# class TestSievePatch(unittest.TestCase):
#
#     def setUp(self):
#         self.base_sieve = Sieve(BASE_PRODUCT)
#
#
#     def test_does_a_patch(self):
#
#         first_dict =  {u"name": u"something",
#                             u"description": u"these are other options",
#                             u"options":{
#                                 u"size": [u"big", u"medium", u"small"],
#                                 u"tool": [u"cnc", u"laser", u"plaster"],
#                                 u"days": [u"tuesday", u"thursday"],
#                                 u"drinks": [u"beer", u"coffee"],
#                                 u"snacks": [u"crisps", u"cheese", u"apple"]
#                             }
#                         }
#
#         expected =  {u"name": u"something",
#                     u"description": u"these are other options",
#                     u"options":{
#                         u"color": [u"red", u"green", u"blue"],
#                         u"size": [u"big", u"medium", u"small"],
#                         u"tool": [u"cnc", u"laser", u"plaster"],
#                         "material": [u"wood", u"metal", u"plastic"],
#                         u"days": [u"tuesday", u"thursday"],
#                         u"drinks": [u"beer", u"coffee"],
#                         u"snacks": [u"crisps", u"cheese", u"apple"]
#                     }
#                 }
#
#         first_sieve = Sieve(first_dict)
#         patched = first_sieve.patch(self.base_sieve)
#         self.maxDiff = None
#         self.assertEqual(patched.get_json(), expected)
#
#
#     def test_match(self):
#
#         configured_product_1 = {u"name": u"cat",
#                    u"description": u"This is a very nice table",
#                    u"options":{
#                         u"color": u"red",
#                         u"size": u"big"
#                    }
#         }
#
#
#         configured_product_2 = {u"name": u"dog",
#                    u"description": u"This is a very nice table",
#                    u"options":{
#                         u"color": u"red",
#                    }
#         }
#
#
#         configured_product_3 = {u"name": u"fish",
#                    u"description": u"This is a very nice table",
#                    u"options":{
#                         u"color": u"red",
#                         u"size": u"old"
#                    }
#         }
#
#         configured_product_4 = {u"name": u"goat",
#                    u"description": u"This is a very nice table",
#                    u"options":{
#                         u"color": [u"red", u"green"],
#                         u"size": u"small"
#                    }
#         }
#
#
#         found = self.base_sieve.match([Sieve(configured_product_1),
#                                        Sieve(configured_product_2),
#                                        Sieve(configured_product_3),
#                                        Sieve(configured_product_4)])
#
#
#         self.assertEqual(set([f.name for f in found]), set([u'cat', u'dog', u'goat']))
#
#
# class TestSieveHistory(unittest.TestCase):
#
#
#     def setUp(self):
#         self.base_sieve = Sieve(BASE_PRODUCT)
#
#
#     def test_does_a_patch(self):
#
#         first_dict =  {u"name": u"something",
#                             u"description": u"these are other options",
#                             u"options":{
#                                 u"size": [u"big", u"medium", u"small"],
#                                 u"tool": [u"cnc", u"laser", u"plaster"],
#                                 u"days": [u"tuesday", u"thursday"],
#                                 u"drinks": [u"beer", u"coffee"],
#                                 u"snacks": [u"crisps", u"cheese", u"apple"]
#                             }
#                         }
#
#         expected =  {u"name": u"something",
#                     u"description": u"these are other options",
#                     u"options":{
#                         u"color": [u"red", u"green", u"blue"],
#                         u"size": [u"big", u"medium", u"small"],
#                         u"tool": [u"cnc", u"laser", u"plaster"],
#                         u"material": [u"wood", u"metal", u"plastic"],
#                         u"days": [u"tuesday", u"thursday"],
#                         u"drinks": [u"beer", u"coffee"],
#                         u"snacks": [u"crisps", u"cheese", u"apple"]
#                     }
#                 }
#
#         first_sieve = Sieve(first_dict)
#         patched = first_sieve.patch(self.base_sieve)
#         self.maxDiff = None
#         self.assertEqual(patched.doc, expected)
#
#
# class TestJsonConversion(unittest.TestCase):
#
#
#     def test_json_load(self):
#
#         as_json = u'{\n    "a": 3.9, \n    "b": 4\n}'
#         loaded = json_loads(as_json)
#         self.assertEqual({'a' : Decimal('3.9'), "b": 4}, loaded)
#
#
#     def test_json_dump(self):
#
#         dump  = json_dumps({'a' : Decimal('3.9'), "b": 4})
#         result = u'{\n    "a": 3.9, \n    "b": 4\n}'
#         self.assertEqual(dump, result)
#
