import unittest
from winnow.utils import json_dumps, json_loads
import winnow
from winnow.models.base import WinnowVersion
from copy import deepcopy
from winnow.exceptions import OptionsExceptionFailedValidation, OptionsExceptionNoAllowed


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

        version = WinnowVersion.add_doc(self.db, BASE_PRODUCT, {})

        broken_option = deepcopy(BASE_PRODUCT)
        broken_option[u"options"] = u"text"

        self.assertRaises(OptionsExceptionFailedValidation, WinnowVersion.add_doc, self.db, broken_option, {})



class TestSieveAllows(unittest.TestCase):


    def setUp(self):
        self.db = MockKVStore()
        self.base_version = WinnowVersion.add_doc(self.db, BASE_PRODUCT, {})


    def test_allows_subset(self):

        configured_option = deepcopy(BASE_PRODUCT)
        configured_option[u"options"][u"color"] = u"red"

        configured_version = WinnowVersion.add_doc(self.db, configured_option, {})
        self.assertTrue(winnow.allows(self.base_version, configured_version))

        configured_option = deepcopy(BASE_PRODUCT)
        configured_option[u"options"][u"color"] = [u"red", u"green"]

        configured_version = WinnowVersion.add_doc(self.db, configured_option, {})
        self.assertTrue(winnow.allows(self.base_version, configured_version))

        configured_option = deepcopy(BASE_PRODUCT)
        configured_option[u"options"][u"color"] = [u"red", u"green"]
        configured_option[u"options"][u"tool"] = [u"cnc"]

        configured_version = WinnowVersion.add_doc(self.db, configured_option, {})
        self.assertTrue(winnow.allows(self.base_version, configured_version))



    def test_allows_subset_without_a_key(self):

        configured_option = deepcopy(BASE_PRODUCT)
        del configured_option[u"options"][u"color"]
        configured_version = WinnowVersion.add_doc(self.db, configured_option, {})
        self.assertTrue(winnow.allows(self.base_version, configured_version))


    def test_allows_subset_with_an_extra_key(self):

        configured_option = deepcopy(BASE_PRODUCT)
        configured_option[u"options"][u"wheels"] = [u"big", u"small"]
        configured_version = WinnowVersion.add_doc(self.db, configured_option, {})


        self.assertTrue(winnow.allows(self.base_version, configured_version))
        self.assertTrue(self.base_version.allows(configured_version))


    def test_allows_fails(self):

        configured_option = deepcopy(BASE_PRODUCT)
        configured_option[u"options"][u"color"] = u"purple"
        configured_version = WinnowVersion.add_doc(self.db, configured_option, {})
        self.assertFalse(winnow.allows(self.base_version, configured_version))
        self.assertFalse(self.base_version.allows(configured_version))



class TestSieveMerge(unittest.TestCase):


    def setUp(self):
        self.db = MockKVStore()
        self.base_version = WinnowVersion.add_doc(self.db, BASE_PRODUCT, {})

    def test_does_a_merge(self):

        other_dict =  {u"name": u"something",
                        u"description": u"these are other options",
                        u"options":{
                            u"color": [u"red", u"blue"],
                            u"size": [u"big", u"medium", u"small"],
                            u"tool": [u"cnc", u"laser", u"plaster"],
                            u"days": [u"tuesday", u"thursday"],
                            u"drinks": [u"beer", u"coffee"],
                            u"snacks": [u"crisps", u"cheese", u"apple"]
                        }
                    }

        expected =  {u"name": u"table",
                    u"description": u"This is a very nice table",
                    u"options":{
                        u"color": [u"blue", u"red"],
                        u"size": [u"big", u"small"],
                        u"tool": [u"cnc", u"laser"],
                        u"material": [u"wood", u"metal", u"plastic"],
                        u"days": [u"tuesday", u"thursday"],
                        u"drinks": [u"beer", u"coffee"],
                        u"snacks": [u"crisps", u"cheese", u"apple"]
                    }
                }

        other_version =  WinnowVersion.add_doc(self.db, other_dict, {})
        merged = WinnowVersion.merged(self.db, BASE_PRODUCT, {}, self.base_version, other_version)

        self.maxDiff = None
        self.assertEqual(merged.kwargs[u"doc"], expected)


class TestSieveExtract(unittest.TestCase):


    def setUp(self):
        self.db = MockKVStore()
        self.base_version = WinnowVersion.add_doc(self.db, BASE_PRODUCT, {})


    def test_can_extract(self):

        to_extract =  {u"name": u"extractions",
                    u"description": u"Only take these keys",
                    u"options":{
                        u"color": None,
                        u"size": None
                    }
                }

        expected =  {u"name": u"table",
                    u"description": u"This is a very nice table",
                    u"options":{
                        u"color": [u"red", u"green", u"blue"],
                        u"size": [u"big", u"small"]
                    }
                }

        extractions = WinnowVersion.add_doc(self.db, to_extract, {})

        extracted = WinnowVersion.extracted(self.db, BASE_PRODUCT, {}, self.base_version, extractions)

        self.maxDiff = None
        self.assertEqual(extracted.kwargs[u"doc"], expected)


class TestSievePatch(unittest.TestCase):

    def setUp(self):
        self.db = MockKVStore()
        self.base_version = WinnowVersion.add_doc(self.db, BASE_PRODUCT, {})

    def test_does_a_patch(self):

        first_dict =  {u"name": u"something",
                            u"description": u"these are other options",
                            u"options":{
                                u"size": [u"big", u"medium", u"small"],
                                u"tool": [u"cnc", u"laser", u"plaster"],
                                u"days": [u"tuesday", u"thursday"],
                                u"drinks": [u"beer", u"coffee"],
                                u"snacks": [u"crisps", u"cheese", u"apple"]
                            }
                        }

        expected =  {u"name": u"something",
                    u"description": u"these are other options",
                    u"options":{
                        u"color": [u"red", u"green", u"blue"],
                        u"size": [u"big", u"medium", u"small"],
                        u"tool": [u"cnc", u"laser", u"plaster"],
                        u"material": [u"wood", u"metal", u"plastic"],
                        u"days": [u"tuesday", u"thursday"],
                        u"drinks": [u"beer", u"coffee"],
                        u"snacks": [u"crisps", u"cheese", u"apple"]
                    }
                }

        first_version =  WinnowVersion.add_doc(self.db, first_dict, {})
        patched = WinnowVersion.patched(self.db, first_dict, {}, first_version, self.base_version)
        self.maxDiff = None
        self.assertEqual(patched.kwargs[u"doc"], expected)




    def test_match(self):

        configured_product_1 = {u"name": u"cat",
                   u"description": u"This is a very nice table",
                   u"options":{
                        u"color": u"red",
                        u"size": u"big"
                   }
        }


        configured_product_2 = {u"name": u"dog",
                   u"description": u"This is a very nice table",
                   u"options":{
                        u"color": u"red",
                   }
        }


        configured_product_3 = {u"name": u"fish",
                   u"description": u"This is a very nice table",
                   u"options":{
                        u"color": u"red",
                        u"size": u"old"
                   }
        }

        configured_product_4 = {u"name": u"goat",
                   u"description": u"This is a very nice table",
                   u"options":{
                        u"color": [u"red", u"green"],
                        u"size": u"small"
                   }
        }

        possible = [WinnowVersion.add_doc(self.db, configured_product_1, {}),
                   WinnowVersion.add_doc(self.db, configured_product_2, {}),
                   WinnowVersion.add_doc(self.db, configured_product_3, {}),
                   WinnowVersion.add_doc(self.db, configured_product_4, {})]

        found = self.base_version.filter_allows(possible)

        self.assertEqual(set([f.kwargs[u"doc"][u"name"] for f in found]), set([u'cat', u'dog', u'goat']))

