import os
import unittest
import json
from decimal import Decimal
from db import MockKVStore
from winnow import product_flow
from sieve.base_sieve import json_loads, json_dumps
from sieve.product_sieve import ProductSieve
from sieve.options_exceptions import OptionsExceptionFailedValidation, OptionsExceptionEmptyOptionValues
from copy import deepcopy
import time

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


with open(os.path.join(DATA_DIR, "product.json"), "r") as f:
    BASE_PRODUCT = json_loads(f.read())

def get_timestamp():
    return unicode(time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()))


class TestPublishingProduct(unittest.TestCase):


    def setUp(self):
        self.maxDiff = None

        self.db = MockKVStore()




    def test_publish_product_sieve(self):

        expected = {
            u"created": get_timestamp(),
            u"history": [[u'start', u'products/lean/cafe-table/standard@e21db383b0fbf2ffd7aa6de951de4feb478a3b83']],
            u'uri': u'products/lean/cafe-table/standard@e21db383b0fbf2ffd7aa6de951de4feb478a3b83',
            u"type": u"product",
            u"doc":{
                u"name": u"Standard",
                u"slug": u"standard",
                u"description": u"A nice cafe table with three legs",
                u"design": u"cafe-table",
                u"range": u"lean",
                u"public": True,
                u"standard": True,
                u"version": [Decimal('0'), Decimal('0'), Decimal('1')],
                u"options": {
                    u"material": {
                        u"description": u"Choose one of the materials",
                        u"name": u"Material",
                        u"type": u"set::string",
                        u"values": [
                            {
                                u"description": u"Everything is made out of ply",
                                u"image_uri": u"http://something.com/khgfdkyg.png",
                                u"name": u"All ply",
                                u"type": u"set::string",
                                u"value": u"all-ply"
                            },
                            {
                                u"description": u"The legs are ply and the top is wisa",
                                u"image_uri": u"http://something.com/khgfdkyg.png",
                                u"name": u"Wisa",
                                u"type": u"set::string",
                                u"value": u"wisa"
                            }
                        ]
                    },
                    u"sheet": {
                        u"description": u"The nominal sheet thickness",
                        u"name": u"Nominal sheet thickness",
                        u"type": u"set::string",
                        u"values": [
                            {
                                u"description": u"18mm ply wood",
                                u"image_uri": u"http://something.com/khgfdkyg.png",
                                u"name": u"18mm",
                                u"type": u"set::string",
                                u"value": u"18mm"
                            },
                            {
                                u"description": u"25mm ply wood",
                                u"image_uri": u"http://something.com/khgfdkyg.png",
                                u"name": u"25mm",
                                u"type": u"set::string",
                                u"value": u"25mm"
                            }
                        ]
                    }
                },
            }
        }

        doc = json_dumps(BASE_PRODUCT)
        product_flow.publish_product(self.db, doc)
        fetched_doc = self.db.get("products/lean/cafe-table/standard")
        fetched = ProductSieve.from_json(fetched_doc)
        self.assertEqual(fetched.get_json(), expected)


class TestPublishingFilesets(unittest.TestCase):


    def setUp(self):
        self.db = MockKVStore()
        self.product = product_flow.publish_product(self.db, json_dumps(BASE_PRODUCT))
        print self.product


    def test_publish_fileset_with_files(self):

        with open(os.path.join(DATA_DIR, "fileset.json"), "r") as f:
            fileset_json = f.read()

        expected = {
                    u"type": u"fileset",
                    u'created': get_timestamp(),
                    u"uri": u"products/lean/cafe-table/standard/filesets/test_fileset@0db3a5369bcbff9d96bd1d87b024094594f0a81d",
                    u'history': [[u'start', u'products/lean/cafe-table/standard/filesets/test_fileset@0db3a5369bcbff9d96bd1d87b024094594f0a81d']],
                    u'product': u"products/lean/cafe-table/standard@e21db383b0fbf2ffd7aa6de951de4feb478a3b83",
                    u"doc":{
                        u"slug": u"test_fileset",
                        u"name": u"Test Fileset",
                        u"version": [Decimal('1'), Decimal('0'), Decimal('1')],
                        u"category": u"sheets",
                        u'product': u"products/lean/cafe-table/standard",
                        u"files": [u"files/test_1.txt", u"files/test_2.txt"],
                        u"description": u"Cad files for 18mm ply",
                        u"options": {
                            u"material": u"all-ply",
                            u"sheet": u"18mm",
                            u"thickness": Decimal('17.9'),
                            u"tolerance": Decimal('0')
                        },
                    }
        }

        product_flow.publish_fileset(self.db, fileset_json)

        fetched_doc = self.db.get(u"products/lean/cafe-table/standard/filesets/test_fileset")
        self.assertIsNotNone(fetched_doc)
        self.maxDiff = None
        self.assertEqual(json_loads(fetched_doc), expected)



class TestContexts(unittest.TestCase):


    def setUp(self):
        self.db = MockKVStore()
        product_flow.publish_product(self.db, json_dumps(BASE_PRODUCT))

    def test_get_contextualised(self):


        with open(os.path.join(DATA_DIR, "context.json"), "r") as f:
            context_json = f.read()

        expected = {
                    u"type": u"product",
                    u'created': get_timestamp(),
                    u'uri': u'products/lean/cafe-table/standard@442d273e52334bb9a4f9e9b6115b2f062babb6cc',
                    u'history': [[u'start', u'products/lean/cafe-table/standard@e21db383b0fbf2ffd7aa6de951de4feb478a3b83'],
                                 [u'merge', u'context/uk_production_context@d68a0e4bcd9bf375b42e4847c416a26f5d3cf023']],
                    u"snapshot": True,
                    u"doc":{
                        u"name": u"Standard",
                        u"slug": u"standard",
                        u"description": u"A nice cafe table with three legs",
                        u"design": u"cafe-table",
                        u"range": u"lean",
                        u"public": True,
                        u"standard": True,
                        u"version": [Decimal('0'), Decimal('0'), Decimal('1')],
                        u"description": u"A nice cafe table with three legs",
                        u"options": {
                            u'color': [u'green', u'blue', u'purple', u'orange'],
                            u"material": {
                                u"description": u"Choose one of the materials",
                                u"name": u"Material",
                                u"type": u"set::string",
                                u"values": {
                                        u"description": u"The legs are ply and the top is wisa",
                                        u"image_uri": u"http://something.com/khgfdkyg.png",
                                        u"name": u"Wisa",
                                        u"type": u"set::string",
                                        u"value": u"wisa"
                                    }
                            },
                            u"sheet": {
                                u"description": u"The nominal sheet thickness",
                                u"name": u"Nominal sheet thickness",
                                u"type": u"set::string",
                                u"values": {
                                        u"description": u"18mm ply wood",
                                        u"image_uri": u"http://something.com/khgfdkyg.png",
                                        u"name": u"18mm",
                                        u"type": u"set::string",
                                        u"value": u"18mm"
                                },
                            }
                        },
                    }
                }

        product_flow.publish_context(self.db, context_json)
        config = product_flow.get_contextualised_product(self.db, u"products/lean/cafe-table/standard", [u"context/uk_production_context"])

        self.maxDiff = None
        self.assertEqual(config.get_json(), expected)


    def test_extraction(self):

        with open(os.path.join(DATA_DIR, "context.json"), "r") as f:
            context_json = f.read()

        expected = {
                    u"type": u"product",
                    u'created': get_timestamp(),
                    u'uri': u'products/lean/cafe-table/standard@cbf056cc1ccc75a2332a91363c284cbc4612f321',
                    u'history': [[u'start', u'products/lean/cafe-table/standard@e21db383b0fbf2ffd7aa6de951de4feb478a3b83'],
                                 [u'merge', u'context/uk_production_context@d68a0e4bcd9bf375b42e4847c416a26f5d3cf023'],
                                 [u"extract", [u"color", u"material"]]],
                    u"snapshot": True,
                    u"doc":{
                        u"name": u"Standard",
                        u"slug": u"standard",
                        u"description": u"A nice cafe table with three legs",
                        u"design": u"cafe-table",
                        u"range": u"lean",
                        u"public": True,
                        u"standard": True,
                        u"version": [Decimal('0'), Decimal('0'), Decimal('1')],
                        u"description": u"A nice cafe table with three legs",
                        u"options": {
                            u'color': [u'green', u'blue', u'purple', u'orange'],
                            u"material": {
                                u"description": u"Choose one of the materials",
                                u"name": u"Material",
                                u"type": u"set::string",
                                u"values": {
                                        u"description": u"The legs are ply and the top is wisa",
                                        u"image_uri": u"http://something.com/khgfdkyg.png",
                                        u"name": u"Wisa",
                                        u"type": u"set::string",
                                        u"value": u"wisa"
                                    }
                            },
                        },
                    }
                }

        product_flow.publish_context(self.db, context_json)
        config = product_flow.get_contextualised_product(self.db, u"products/lean/cafe-table/standard", [u"context/uk_production_context"], extractions=[u"color", u"material"])

        self.maxDiff = None
        self.assertEqual(config.get_json(), expected)


    def test_get_config(self):

        with open(os.path.join(DATA_DIR, "context.json"), "r") as f:
            context_json = f.read()

        expected = {
                        u"name": u"Standard",
                        u"slug": u"standard",
                        u"description": u"A nice cafe table with three legs",
                        u"design": u"cafe-table",
                        u"range": u"lean",
                        u"public": True,
                        u"standard": True,
                        u"version": [Decimal('0'), Decimal('0'), Decimal('1')],
                        u"description": u"A nice cafe table with three legs",
                        u"options": {
                            u'color': [u'green', u'blue', u'purple', u'orange'],
                            u"material": {
                                u"description": u"Choose one of the materials",
                                u"name": u"Material",
                                u"type": u"set::string",
                                u"values": {
                                        u"description": u"The legs are ply and the top is wisa",
                                        u"image_uri": u"http://something.com/khgfdkyg.png",
                                        u"name": u"Wisa",
                                        u"type": u"set::string",
                                        u"value": u"wisa"
                                    }
                            },
                        },
                    }

        product_flow.publish_context(self.db, context_json)
        config = product_flow.get_configuration_json(self.db, u"products/lean/cafe-table/standard", [u"context/uk_production_context"])
        self.maxDiff = None
        self.assertEqual(json_loads(config), expected)


    def test_get_contextualised_many(self):

        with open(os.path.join(DATA_DIR, "context.json"), "r") as f:
            context_json = f.read()

        with open(os.path.join(DATA_DIR, "tolerance_context.json"), "r") as f:
            tolerance_context_json = f.read()

        expected = {
                    u"type": u"product",
                    u'created': get_timestamp(),
                    u'uri': u'products/lean/cafe-table/standard@5e2e540d860f8312b526bd3624b99d5cb289f547',
                    u'history': [[u'start', u'products/lean/cafe-table/standard@e21db383b0fbf2ffd7aa6de951de4feb478a3b83'],
                                 [u'merge', u'context/uk_production_context@d68a0e4bcd9bf375b42e4847c416a26f5d3cf023'],
                                 [u'merge', u'context/ply_18.1mm@96b1e4cdf3acea6d6a4f1f93acf0511479b73ceb']],
                    u"snapshot": True,
                    u"doc":{
                        u"name": u"Standard",
                        u"slug": u"standard",
                        u"description": u"A nice cafe table with three legs",
                        u"design": u"cafe-table",
                        u"range": u"lean",
                        u"public": True,
                        u"standard": True,
                        u"version": [Decimal('0'), Decimal('0'), Decimal('1')],
                        u"description": u"A nice cafe table with three legs",
                        u"options": {
                            u'color': [u'green', u'blue', u'purple', u'orange'],
                            u"material": {
                                u"description": u"Choose one of the materials",
                                u"name": u"Material",
                                u"type": u"set::string",
                                u"values": {
                                        u"description": u"The legs are ply and the top is wisa",
                                        u"image_uri": u"http://something.com/khgfdkyg.png",
                                        u"name": u"Wisa",
                                        u"type": u"set::string",
                                        u"value": u"wisa"
                                    }
                            },
                            u"sheet": {
                                u"description": u"The nominal sheet thickness",
                                u"name": u"Nominal sheet thickness",
                                u"type": u"set::string",
                                u"values": {
                                        u"description": u"18mm ply wood",
                                        u"image_uri": u"http://something.com/khgfdkyg.png",
                                        u"name": u"18mm",
                                        u"type": u"set::string",
                                        u"value": u"18mm"
                                },
                            },
                            u'thickness': Decimal('18.1')
                        },
                    }
                }

        product_flow.publish_context(self.db, context_json)
        product_flow.publish_context(self.db, tolerance_context_json)

        config = product_flow.get_contextualised_product(self.db, u"products/lean/cafe-table/standard", [u"context/uk_production_context", u"context/ply_18.1mm"])

        self.maxDiff = None
        self.assertEqual(config.get_json(), expected)


    def test_get_quantified_configuration(self):

        with open(os.path.join(DATA_DIR, "context.json"), "r") as f:
            context_json = f.read()

        choice_json = {
                        u"name": u"Standard",
                        u"slug": u"standard",
                        u"description": u"A nice cafe table with three legs",
                        u"design": u"cafe-table",
                        u"range": u"lean",
                        u"public": True,
                        u"standard": True,
                        u"version": [Decimal('0'), Decimal('0'), Decimal('1')],
                        u"description": u"A nice cafe table with three legs",
                        u"options": {
                            u'color': u'green',
                            u"material":  u"wisa",
                        },
                    }

        expected = {u"type": u"product",
                    u'created': get_timestamp(),
                    u'uri': u'products/lean/cafe-table/standard@dd65b2702089bdf7e9ce3c77e5b00eb92ee75d26',
                    u'history': [[u'start', u'products/lean/cafe-table/standard@e21db383b0fbf2ffd7aa6de951de4feb478a3b83'],
                                 [u'merge', u'products/lean/cafe-table/standard@ad56baea886747c7deb395a3df6f36b09ba88813'],
                                 [u'merge', u'context/uk_production_context@d68a0e4bcd9bf375b42e4847c416a26f5d3cf023']],
                    u"snapshot": True,
                    u"doc":{
                        u"name": u"Standard",
                        u"slug": u"standard",
                        u"description": u"A nice cafe table with three legs",
                        u"design": u"cafe-table",
                        u"range": u"lean",
                        u"public": True,
                        u'quantity': 2,
                        u"standard": True,
                        u"version": [Decimal('0'), Decimal('0'), Decimal('1')],
                        u"description": u"A nice cafe table with three legs",
                        u"options": {
                            u'color': u'green',
                            u"sheet": {
                                u"description": u"The nominal sheet thickness",
                                u"name": u"Nominal sheet thickness",
                                u"type": u"set::string",
                                u"values": {
                                        u"description": u"18mm ply wood",
                                        u"image_uri": u"http://something.com/khgfdkyg.png",
                                        u"name": u"18mm",
                                        u"type": u"set::string",
                                        u"value": u"18mm"
                                },
                            },
                            u"material": {
                                u"description": u"Choose one of the materials",
                                u"name": u"Material",
                                u"type": u"set::string",
                                u"values": {
                                        u"description": u"The legs are ply and the top is wisa",
                                        u"image_uri": u"http://something.com/khgfdkyg.png",
                                        u"name": u"Wisa",
                                        u"type": u"set::string",
                                        u"value": u"wisa"
                                    }
                            },
                        },
                    }
                }

        product_flow.publish_context(self.db, context_json)
        quantified_configuration = product_flow.get_quantified_configuration(self.db, json_dumps(choice_json), [u"context/uk_production_context"], 2)
        self.maxDiff = None
        self.assertEqual(quantified_configuration.get_json(), expected)


# class TestFindingFilesets(unittest.TestCase):
#
#
#     def setUp(self):
#         self.db = MockKVStore()
#         self.table = product_flow.publish_product(self.db, json.dumps(BASE_PRODUCT))
#
#         CHAIR_PRODUCT =  {u"range": u"paul",
#                     u"design": u"office",
#                     u"name": u"chair",
#                     u"version": [0, 2, 3],
#                     u"description": u"This is a very nice table",
#                     u"options":{
#                         u"configuration":{
#                             u"color": [u"red", u"green", u"blue"],
#                             u"size": [u"big", u"small"]
#                         },
#                         u"manufacturing":{
#                             u"tool": [u"cnc", u"laser"],
#                             u"material": [u"wood", u"metal", u"plastic"]
#                         }
#                     }
#                 }
#
#         self.chair = product_flow.publish_product(self.db, json.dumps(CHAIR_PRODUCT))
#
#         fileset_dict_1 = {u"name": u"ply",
#                     u"product": u"product/paul/office/table",
#                     u"description": u"how to make table from ply",
#                     u"files": [{u"file_one.txt": u"a_file_hash"}, {u"file_two.txt": u"a_file_hash"}],
#                     u"options":{
#                         u"configuration":{
#                             u"color": [u"red", u"green", u"blue"],
#                             u"size": u"big"
#                         },
#                         u"manufacturing":{
#                             u"tool": u"cnc",
#                             u"material": u"wood"
#                         }
#                     }
#         }
#
#         fileset_dict_2 = {u"name": u"ply",
#                     u"product": u"product/paul/office/table",
#                     u"description": u"how to make table from ply",
#                     u"files": [{u"file_one.txt": u"a_file_hash"}, {u"file_two.txt": u"a_file_hash"}],
#                     u"options":{
#                         u"configuration":{
#                             u"color": [u"red", u"green", u"blue"],
#                             u"size": u"big"
#                         },
#                         u"manufacturing":{
#                             u"tool": u"cnc",
#                             u"material": u"metal"
#                         }
#                     }
#         }
#
#         fileset_dict_3 = {u"name": u"ply",
#                     u"product": u"product/paul/office/table",
#                     u"description": u"how to make table from ply",
#                     u"files": [{u"file_one.txt": u"a_file_hash"}, {u"file_two.txt": u"a_file_hash"}],
#                     u"quantity": 2,
#                     u"options":{
#                         u"configuration":{
#                             u"color": [u"red", u"green", u"blue"],
#                             u"size": u"big"
#                         },
#                         u"manufacturing":{
#                             u"tool": u"cnc",
#                             u"material": [u"wood"]
#                         }
#                     }
#         }
#
#         fileset_dict_4 = {u"name": u"ply",
#                     u"product": u"product/paul/office/chair",
#                     u"description": u"how to make table from ply",
#                     u"files": [{u"file_one.txt": u"a_file_hash"}, {u"file_two.txt": u"a_file_hash"}],
#                     u"options":{
#                         u"configuration":{
#                             u"color": [u"red", u"green", u"blue"],
#                             u"size": u"big"
#                         },
#                         u"manufacturing":{
#                             u"tool": u"cnc",
#                             u"material": u"metal"
#                         }
#                     }
#         }
#
#         product_flow.publish_fileset(self.db, json.dumps(fileset_dict_1))
#         product_flow.publish_fileset(self.db, json.dumps(fileset_dict_2))
#         product_flow.publish_fileset(self.db, json.dumps(fileset_dict_3))
#         product_flow.publish_fileset(self.db, json.dumps(fileset_dict_4))
#
#
#     def test_get_filesets(self):
#
#         possible_filesets = self.table.all_canonical_filesets(self.db)
#         self.assertEqual(len(possible_filesets), 3)
#         possible_filesets = self.chair.all_canonical_filesets(self.db)
#         self.assertEqual(len(possible_filesets), 1)
#
#
#     def test_get_filesets(self):
#
#         quantified_config_json = {u"type": u"product",
#                     u'created': get_timestamp(),
#                     u'uri': u'product/paul/office/table@9756c7d2a375f786754e96f6baca4ddbbd550f82',
#                     u'snapshot': True,
#                     u'history': [[u'start', u'product/paul/office/table@e1fc779995c82d9fe65c18008709b2929d799517'],
#                                  [u'merge', u'product/paul/office/table@8251cfaa2f86fbd798a9f8e21a1fb72f4d1db7dd'],
#                                 [u'merge', u'context/uk_production_context@276359e7ce5d1097d4f3c57b143ca9a55507e527']],
#                     u"doc":{
#                         u"range": u"paul",
#                         u'quantity': 2,
#                         u"description": u"This is a very nice table",
#                         u"design": u"office",
#                         u"name": u"table",
#                         u"version": [0, 2, 3],
#                         u"options":{
#                             u"configuration":{
#                                 u"color": [u"blue"],
#                                 u"size": [u"big"],
#                                 u"finish": [u"matt"]
#                             },
#                             u'manufacturing': {
#                                 u'material': [u'metal', u'wood'],
#                                 u'tool': [u'cnc']
#                             }
#                         }
#                     }
#                 }
#
#         quantified_config = ProductSieve.from_json(json.dumps(quantified_config_json))
#         quantified_config.save(self.db)
#
#         found = product_flow.find_file_sets(self.db, u'product/paul/office/table@9756c7d2a375f786754e96f6baca4ddbbd550f82', [])
#
#         self.assertEqual(len(found), 3)
#
#         context_dict1 = {u"name": u"metal_only",
#                     u"description": u"make things from metal",
#                     u"options":{
#                         u"manufacturing":{
#                             u"material": u"metal"
#                         }
#                     }
#         }
#
#         context_dict2 = {u"name": u"wood_only",
#                     u"description": u"make things from wood",
#                     u"options":{
#                       u"manufacturing":{
#                             u"material": u"wood"
#                         }
#                     }
#         }
#
#         product_flow.publish_context(self.db, json.dumps(context_dict1))
#         product_flow.publish_context(self.db, json.dumps(context_dict2))
#
#         found = product_flow.find_file_sets(self.db, u'product/paul/office/table@9756c7d2a375f786754e96f6baca4ddbbd550f82', [u"context/wood_only"])
#         self.assertEqual(len(found), 2)
#
#         found = product_flow.find_file_sets(self.db, u'product/paul/office/table@9756c7d2a375f786754e96f6baca4ddbbd550f82', [u"context/metal_only"])
#         self.assertEqual(len(found), 1)

"""

move doc into its own dict in the json
do doc hashing

"""