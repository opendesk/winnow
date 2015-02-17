import time
import unittest
from winnow.models.base import WinnowVersion
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

        expected =  {   u'history': [[u'start', u'f9ad2b8ed73bbcc28d18e29601da3fd18801fbca'],
                                    [u'merge', u'6700a4528488ad3736c3ad01648a282dd0ef0ef3']],
                        u'uuid': u"123456789",
                        u'doc_hash': u'81ea3a410b8f2baf8151936aa3af17adc4fbc25b',
                        u"doc": {u"name": u"table",
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
                    }


        other_version =  WinnowVersion.add_doc(self.db, other_dict, {})

        merged = WinnowVersion.merged(self.db, BASE_PRODUCT, {}, self.base_version, other_version)
        merged.kwargs[u"uuid"] = u"123456789"

        self.maxDiff = None
        self.assertEqual(merged.kwargs, expected)




#
# class TestSieveExtract(unittest.TestCase):
#
#     def setUp(self):
#         self.base_sieve = PublishedSieve(BASE_PRODUCT)
#
#
#     def test_can_extract(self):
#
#         expected =  {
#                     u"type": u"base",
#                     u"add_docd": get_timestamp(),
#                     u'history': [[u'start', u'base/table@14ce7c80b1563e38bdbf1ce33f4d07603dfc8520'],
#                                  [u"extract", [u"color", u"size"]]],
#                     u'uri': u'base/table@8c4e3238ac1c6d53167e9cb3c924a67ed670b086',
#                     u"doc":{
#                     u"name": u"table",
#                         u"description": u"This is a very nice table",
#                         u"options":{
#                             u"color": [u"red", u"green", u"blue"],
#                             u"size": [u"big", u"small"]
#                         }
#                     }
#                 }
#
#         extracted = self.base_sieve.extract([u"color", u"size"])
#         self.maxDiff = None
#         self.assertEqual(extracted.get_json(), expected)
#
#
#
class TestSievePatch(unittest.TestCase):

    def setUp(self):
        self.db = MockKVStore()
        self.base_version = WinnowVersion.add_doc(self.db, BASE_PRODUCT, {})


    def test_does_a_patch(self):

        target_dict =  {u"name": u"something",
                            u"description": u"these are other options",
                            u"options":{
                                u"size": [u"big", u"medium", u"small"],
                                u"tool": [u"cnc", u"laser", u"plaster"],
                                u"days": [u"tuesday", u"thursday"],
                                u"drinks": [u"beer", u"coffee"],
                                u"snacks": [u"crisps", u"cheese", u"apple"]
                            }
                        }

        expected =  {
                    u'history': [[u'start', u'f9ad2b8ed73bbcc28d18e29601da3fd18801fbca'],
                                [u'patch', u'6db8eee3c6012e891d35689aaf3a97d9d24a2dd7']],
                    u'uuid': u"123456789",
                    u'doc_hash': u'733c4dbd69e82fedb1dd0f9fce9f93aac9366944',
                    u"doc":{
                        u"name": u"table",
                        u"description": u"This is a very nice table",
                        u"options":{
                            u"color": [u"red", u"green", u"blue"],
                            u"size": [u"big", u"small"],
                            u"tool": [u"cnc", u"laser"],
                            u"material": [u"wood", u"metal", u"plastic"],
                            u"days": [u"tuesday", u"thursday"],
                            u"drinks": [u"beer", u"coffee"],
                            u"snacks": [u"crisps", u"cheese", u"apple"]
                        }
                    }
                }


        other_version =  WinnowVersion.add_doc(self.db, target_dict, {})

        merged = WinnowVersion.patched(self.db, BASE_PRODUCT, {}, self.base_version, other_version)
        merged.kwargs[u"uuid"] = u"123456789"

        self.maxDiff = None
        self.assertEqual(expected, merged.kwargs)



class TestSieveFreeze(unittest.TestCase):

    def setUp(self):

        self.db = MockKVStore()

        BASE_PRODUCT_UPSTREAM =  {u"name": u"table",
                    u"description": u"This is a very nice table",
                    u"upstream": u"987654321",
                    u"options":{
                        u"color": [u"red", u"green", u"blue"],
                        u"size": [u"big", u"small"],
                        u"tool": [u"cnc", u"laser"],
                        u"material": [u"wood", u"metal", u"plastic"]
                    }
                }

        self.base_version = WinnowVersion.add_doc(self.db, BASE_PRODUCT_UPSTREAM, {})


    def test_can_expand(self):

        parent_dict = {
                            u"name": u"parent",
                            u"description": u"these are other options",
                            u"options":{
                                u"size": [u"big", u"medium", u"small"],
                                u"tool": [u"cnc", u"laser", u"plaster"],
                                u"days": [u"tuesday", u"thursday"],
                                u"drinks": [u"beer", u"coffee"],
                                u"snacks": [u"crisps", u"cheese", u"apple"]
                            }
                        }

        expected =  {
                    u'history': [[u'start', u'01d4fbbb3ba6f371f29442ac4512af21c7be0016'],
                                [u'patch', u'70fcda78282d52c1613f14180f6fcdfdc4e21533']],
                    u'uuid': u"123456789",
                    u'doc_hash': u'7bdd56c45ae4109c1318058a298dea90392dc2c8',
                    u"is_expanded": True,
                    u"doc":{
                        u"name": u"table",
                        u'upstream': u'987654321',
                        u"description": u"This is a very nice table",
                        u"options":{
                            u"color": [u"red", u"green", u"blue"],
                            u"size": [u"big", u"small"],
                            u"tool": [u"cnc", u"laser"],
                            u"material": [u"wood", u"metal", u"plastic"],
                            u"days": [u"tuesday", u"thursday"],
                            u"drinks": [u"beer", u"coffee"],
                            u"snacks": [u"crisps", u"cheese", u"apple"]
                        }
                    }
                }

        WinnowVersion.add_doc(self.db, parent_dict, {u'uuid': u"987654321"})

        expanded = self.base_version.expanded()

        expanded.kwargs[u"uuid"] = u"123456789"

        self.maxDiff = None
        self.assertEqual(expected, expanded.kwargs)


    def test_can_freeze_two(self):

        grand_parent_dict =  {u"name": u"grandad",
                            u"description": u"this is an older one",
                            u"options":{
                                u"size": [u"big", u"medium", u"small"],
                                u"tool": [u"cnc", u"laser", u"plaster"],
                                u"days": [u"tuesday", u"thursday"],
                                u"drinks": [u"beer", u"coffee"],
                                u"snacks": [u"crisps", u"cheese", u"apple"]
                            }
                        }

        parent_dict =  {u"name": u"parent",
                        u"upstream": u"4321",
                            u"description": u"these are other options",
                            u"options":{
                                u"size": [u"big", u"medium", u"small"],
                                u"tool": [u"cnc", u"laser", u"plaster"],
                                u"drinks": [u"beer", u"coffee", u"water"],
                            }
                        }

        expected =  {
                    u'history': [[u'start', u'01d4fbbb3ba6f371f29442ac4512af21c7be0016'],
                                 [u'patch', u'75bd722148904057bddbdb0785c78317b2cbbd93'],
                                 [u'patch', u'6801083f91450fe2bf5fb88f333bea37bf6c0c38']],
                    u'uuid': u"123456789",
                    u'doc_hash': u'111bd7d92e170466f36fb7c738482457f8de8512',
                    u"is_expanded": True,
                    u"doc":{
                        u"name": u"table",
                        u"description": u"This is a very nice table",
                        u'upstream': u'987654321',
                        u"options":{
                            u"color": [u"red", u"green", u"blue"],
                            u"size": [u"big", u"small"],
                            u"tool": [u"cnc", u"laser"],
                            u"material": [u"wood", u"metal", u"plastic"],
                            u"days": [u"tuesday", u"thursday"],
                            u"drinks": [u"beer", u"coffee", u"water"],
                            u"snacks": [u"crisps", u"cheese", u"apple"]
                        }
                    }
                }

        WinnowVersion.add_doc(self.db, parent_dict, {u'uuid': u"987654321"})
        WinnowVersion.add_doc(self.db, grand_parent_dict, {u'uuid': u"4321"})

        expanded = self.base_version.expanded()

        expanded.kwargs[u"uuid"] = u"123456789"

        self.maxDiff = None
        self.assertEqual(expected, expanded.kwargs)
