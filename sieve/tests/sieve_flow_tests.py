import unittest
import json
from sieve.product_sieve import ProductSieve
from db import MockKVStore
from sieve import product_flow
from sieve.product_exceptions import ProductExceptionFailedValidation, ProductExceptionEmptyOptionValues
from copy import deepcopy
import time

BASE_PRODUCT =  {u"range": u"paul",
                    u"design": u"office",
                    u"name": u"table",
                    u"version": [0, 2, 3],
                    u"description": u"This is a very nice table",
                    u"options":{
                        u"configuration":{
                            u"color": [u"red", u"green", u"blue"],
                            u"size": [u"big", u"small"]
                        },
                        u"manufacturing":{
                            u"tool": [u"cnc", u"laser"],
                            u"material": [u"wood", u"metal", u"plastic"]
                        }
                    }
                }


def get_timestamp():
    return unicode(time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()))


class TestPublishingProduct(unittest.TestCase):


    def setUp(self):
        self.maxDiff = None

        self.db = MockKVStore()


    def test_validates_product_sieve(self):

        ProductSieve(BASE_PRODUCT)

        broken_option = deepcopy(BASE_PRODUCT)
        broken_option[u"options"][u"configuration"] = u"text"

        self.assertRaises(ProductExceptionFailedValidation, ProductSieve, broken_option)

        broken_option = deepcopy(BASE_PRODUCT)
        del broken_option[u"design"]

        self.assertRaises(ProductExceptionFailedValidation, ProductSieve, broken_option)

        broken_option = deepcopy(BASE_PRODUCT)
        del broken_option[u"range"]

        self.assertRaises(ProductExceptionFailedValidation, ProductSieve, broken_option)

        broken_option = deepcopy(BASE_PRODUCT)
        del broken_option[u"version"]

        self.assertRaises(ProductExceptionFailedValidation, ProductSieve, broken_option)

        broken_option = deepcopy(BASE_PRODUCT)
        broken_option[u"version"][2] = u"v"

        self.assertRaises(ProductExceptionFailedValidation, ProductSieve, broken_option)


    def test_publish_product_sieve(self):

        expected = {
            u"created": get_timestamp(),
            u"history": [[u'start', u'product/paul/office/table@e1fc779995c82d9fe65c18008709b2929d799517']],
            u'uri': u'product/paul/office/table@666f541b28d752a2ec738a3c691ec4d189094d66',
            u"type": u"product",
            u"doc":{
                u"name": u"table",
                u"description": u"This is a very nice table",
                u"design": u"office",
                u"range": u"paul",
                u"version": [0, 2, 3],
                u"options": {
                    u"configuration": {
                        u"color": [u"red", u"green", u"blue"],
                        u"size": [u"big", u"small"]
                    },
                    u"manufacturing": {
                        u"material": [u"wood", u"metal", u"plastic"],
                        u"tool": [u"cnc", u"laser"]
                    }
                }
            }
        }

        doc = json.dumps(BASE_PRODUCT)

        product_flow.publish_product(self.db, doc)
        fetched_doc = self.db.get("product/paul/office/table")
        fetched = ProductSieve.from_json(fetched_doc)
        self.assertEqual(fetched.get_json(), expected)


class TestPublishingFilesets(unittest.TestCase):


    def setUp(self):
        self.db = MockKVStore()
        self.product = product_flow.publish_product(self.db, json.dumps(BASE_PRODUCT))
        print self.product


    def test_publish_fileset_with_files(self):

        fileset_dict = {u"name": u"ply",
                    u"product": u"product/paul/office/table",
                    u"description": u"how to make table from ply",
                    u"files": [{u"file_one.txt": u"a_file_hash"}, {u"file_two.txt": u"a_file_hash"}],
                    u"options":{
                        u"configuration":{
                            u"color": [u"red", u"green", u"blue"],
                            u"size": u"big"
                        },
                        u"manufacturing":{
                            u"tool": u"cnc",
                            u"material": [u"wood", u"metal"]
                        }
                    }
        }


        expected = {
                    u"type": u"fileset",
                    u'created': get_timestamp(),
                    u"uri": u"fileset/paul/office/table/ply/ply@ceaa58e3e932ba3bc11c8df05ba06ea1344b0a03",
                    u'history': [[u'start', u'fileset/paul/office/table/ply/ply@ceaa58e3e932ba3bc11c8df05ba06ea1344b0a03']],
                    u'product': u'product/paul/office/table',
                    u"doc":{
                        u"name": u"ply",
                        u'product': u"product/paul/office/table@666f541b28d752a2ec738a3c691ec4d189094d66",
                        u"files": [{u"file_one.txt": u"a_file_hash"}, {u"file_two.txt": u"a_file_hash"}],
                        u"description": u"how to make table from ply",
                        u"options":{
                            u"configuration":{
                                u"color": [u"red", u"green", u"blue"],
                                u"size": u"big"
                            },
                            u"manufacturing":{
                                u"tool": u"cnc",
                                u"material": [u"wood", u"metal"]
                            }
                        }
                    }
        }

        fileset_json = json.dumps(fileset_dict)
        product_flow.publish_fileset(self.db, fileset_json)

        fetched_doc = self.db.get(u"fileset/paul/office/table/ply/ply")
        self.maxDiff = None
        self.assertEqual(json.loads(fetched_doc), expected)



class TestContexts(unittest.TestCase):


    def setUp(self):
        self.db = MockKVStore()
        product_flow.publish_product(self.db, json.dumps(BASE_PRODUCT))

    def test_get_contextualised(self):

        context_dict = {u"name": u"uk_production_context",
                    u"description": u"things that are possible in the uk",
                    u"options":{
                        u"configuration":{
                            u"color": [u"green", u"blue", u"purple", u"orange"],
                            u"size": u"big",
                            u"finish": [u"shiney", u"matt"]
                        },
                        u"manufacturing":{
                            u"tool": [u"cnc", u"casting"],
                            u"material": [u"wood", u"metal"]
                        }
                    }
        }

        expected = {
                    u"type": u"product",
                    u'created': get_timestamp(),
                    u'uri': u'product/paul/office/table@6b646d28e46932ab8fadf5c8d242c39a9954b2b0',
                    u'history': [[u'start', u'product/paul/office/table@e1fc779995c82d9fe65c18008709b2929d799517'],
                                 [u'merge', u'context/uk_production_context@276359e7ce5d1097d4f3c57b143ca9a55507e527']],
                    u"snapshot": True,
                    u"doc":{
                        u"name": u"table",
                        u"range": u"paul",
                        u"design": u"office",
                        u"version": [0, 2, 3],
                        u"description": u"This is a very nice table",
                        u"options":{
                            u"configuration":{
                                u"color": [u"blue", u"green"],
                                u"size": [u"big"],
                                u"finish": [u"shiney", u"matt"]
                            },
                           u"manufacturing":{
                                u"tool": [u"cnc"],
                                u"material": [u"metal", u"wood"]
                            }
                        }
                    }
                }

        product_flow.publish_context(self.db, json.dumps(context_dict))
        config = product_flow.get_contextualised_product(self.db, u"product/paul/office/table", [u"context/uk_production_context"])
        self.maxDiff = None
        self.assertEqual(config.get_json(), expected)


    def test_extraction(self):

        context_dict = {u"name": u"uk_production_context",
                    u"description": u"things that are possible in the uk",
                    u"options":{
                        u"configuration":{
                            u"color": [u"green", u"blue", u"purple", u"orange"],
                            u"size": u"big",
                            u"finish": [u"shiney", u"matt"]
                        },
                        u"manufacturing":{
                            u"tool": [u"cnc", u"casting"],
                            u"material": [u"wood", u"metal"]
                        }
                    }
        }

        expected = {
                    u"type": u"product",
                    u'created': get_timestamp(),
                    u'uri': u'product/paul/office/table@da4737af28413c87c2a9ebef6a935045e7902475',
                    u'snapshot': True,
                    u'history': [[u'start', u'product/paul/office/table@e1fc779995c82d9fe65c18008709b2929d799517'],
                                [u'merge', u'context/uk_production_context@276359e7ce5d1097d4f3c57b143ca9a55507e527'],
                                [u'extract', [u'configuration']]],
                    u"doc": {
                        u"range": u"paul",
                        u"design": u"office",
                        u"name": u"table",
                        u"version": [0, 2, 3],
                        u"description": u"This is a very nice table",
                        u"options":{
                            u"configuration":{
                                u"color": [u"blue", u"green"],
                                u"size": [u"big"],
                                u"finish": [u"shiney", u"matt"]
                            }
                        }
                    }
                }

        product_flow.publish_context(self.db, json.dumps(context_dict))
        config = product_flow.get_contextualised_product(self.db, u"product/paul/office/table", [u"context/uk_production_context"], extractions=[u"configuration"])
        self.maxDiff = None
        self.assertEqual(config.get_json(), expected)


    def test_get_config(self):

        context_dict = {u"name": u"uk_production_context",
                    u"description": u"things that are possible in the uk",
                    u"options":{
                        u"configuration":{
                            u"color": [u"green", u"blue", u"purple", u"orange"],
                            u"size": u"big",
                            u"finish": [u"shiney", u"matt"]
                        },
                        u"manufacturing":{
                            u"tool": [u"cnc", u"casting"],
                            u"material": [u"wood", u"metal"]
                        }
                    }
        }

        expected = {u"range": u"paul",
                    u"design": u"office",
                    u"name": u"table",
                    u"version": [0, 2, 3],
                    u"description": u"This is a very nice table",
                    u"options":{
                        u"configuration":{
                            u"color": [u"blue", u"green"],
                            u"size": [u"big"],
                            u"finish": [u"shiney", u"matt"]
                        }
                    }
                }

        product_flow.publish_context(self.db, json.dumps(context_dict))
        config = product_flow.get_configuration_json(self.db, u"product/paul/office/table", [u"context/uk_production_context"])
        self.maxDiff = None
        self.assertEqual(json.loads(config), expected)


    def test_get_contextualised_many(self):

        context_dict1 = {u"name": u"uk_production_context",
                    u"description": u"things that are possible in the uk",
                    u"options":{
                        u"configuration":{
                            u"color": [u"green", u"blue", u"purple", u"orange"],
                            u"size": u"big",
                            u"finish": [u"shiney", u"matt"]
                        },
                        u"manufacturing":{
                            u"tool": [u"cnc", u"casting"],
                            u"material": [u"wood", u"metal"]
                        }
                    }
        }

        context_dict2 = {u"name": u"tue_production_context",
                    u"description": u"things that are possible on tuesdays",
                    u"options":{
                        u"configuration":{
                            u"color": [u"green", u"red"],
                            u"finish": [u"shiney", u"matt", u"sandblasted"]
                        },
                        u"delivery":{
                            u"days": [u"monday", u"tuesday", u"wednesday"],
                            u"method": [u"hand", u"post"]
                        }
                    }
        }

        expected = {
                    u"type": u"product",
                    u'created': get_timestamp(),
                    u'uri': u'product/paul/office/table@5ed13220ee6ecc14f1e77e29046996ff8b3e4be9',
                    u'snapshot': True,
                    u'history': [[u'start', u'product/paul/office/table@e1fc779995c82d9fe65c18008709b2929d799517'],
                        [u'merge', u'context/uk_production_context@276359e7ce5d1097d4f3c57b143ca9a55507e527'],
                        [u'merge', u'context/tue_production_context@8c0a5295b7c7d93353d4d0d3f82b5063454165a7']],
                    u"doc": {
                        u"name": u"table",
                        u"range": u"paul",
                        u"design": u"office",
                        u"version": [0, 2, 3],
                        u"description": u"This is a very nice table",
                        u"options":{
                            u"configuration":{
                                u"color": [u"green"],
                                u"size": [u"big"],
                                u"finish": [u"matt", u"shiney"]
                            },
                           u"manufacturing":{
                                u"tool": [u"cnc"],
                                u"material": [u"metal", u"wood"]
                            },
                            u"delivery":{
                                u"days": [u"monday", u"tuesday", u"wednesday"],
                                u"method": [u"hand", u"post"]
                            }
                        }
                    }
                }

        product_flow.publish_context(self.db, json.dumps(context_dict1))
        product_flow.publish_context(self.db, json.dumps(context_dict2))

        config = product_flow.get_contextualised_product(self.db,
                                                         u"product/paul/office/table",
                                                         [u"context/uk_production_context", u"context/tue_production_context"])
        self.maxDiff = None
        self.assertEqual(config.get_json(), expected)


    def test_fail_impossible_merge(self):

        context_dict1 = {u"name": u"uk_production_context",
                    u"description": u"things that are possible in the uk",
                    u"options":{
                        u"configuration":{
                            u"color": [u"green", u"blue", u"purple", u"orange"],
                            u"size": u"big",
                            u"finish": [u"shiney", u"matt"]
                        },
                        u"manufacturing":{
                            u"tool": [u"cnc", u"casting"],
                            u"material": [u"wood", u"metal"]
                        }
                    }
        }

        context_dict2 = {u"name": u"tue_production_context",
                    u"description": u"things that are possible on tuesdays",
                    u"options":{
                        u"configuration":{
                            u"color": [u"red", u"pink"],
                            u"finish": [u"shiney", u"matt", u"sandblasted"]
                        },
                        u"delivery":{
                            u"days": [u"monday", u"tuesday", u"wednesday"],
                            u"method": [u"hand", u"post"]
                        }
                    }
        }

        product_flow.publish_context(self.db, json.dumps(context_dict1))
        product_flow.publish_context(self.db, json.dumps(context_dict2))

        self.assertRaises(ProductExceptionEmptyOptionValues,
                          product_flow.get_contextualised_product,
                          self.db,
                          u"product/paul/office/table",
                          [u"context/uk_production_context", u"context/tue_production_context"])


    def test_get_quantified_configuration(self):


        context_dict = {u"name": u"uk_production_context",
                    u"description": u"things that are possible in the uk",
                    u"options":{
                        u"configuration":{
                            u"color": [u"green", u"blue", u"purple", u"orange"],
                            u"size": u"big",
                            u"finish": [u"shiney", u"matt"]
                        },
                        u"manufacturing":{
                            u"tool": [u"cnc", u"casting"],
                            u"material": [u"wood", u"metal"]
                        }
                    }
        }

        choice_json = {u"range": u"paul",
            u"design": u"office",
            u"name": u"table",
            u"version": [0, 2, 3],
            u"description": u"This is a very nice table",
            u"options":{
                u"configuration":{
                    u"color": [u"blue"],
                    u"size": [u"big"],
                    u"finish": [u"matt"]
                }
            }
        }

        expected = {u"type": u"product",
                    u'created': get_timestamp(),
                    u'uri': u'product/paul/office/table@9756c7d2a375f786754e96f6baca4ddbbd550f82',
                    u'snapshot': True,
                    u'history': [[u'start', u'product/paul/office/table@e1fc779995c82d9fe65c18008709b2929d799517'],
                                 [u'merge', u'product/paul/office/table@8251cfaa2f86fbd798a9f8e21a1fb72f4d1db7dd'],
                                [u'merge', u'context/uk_production_context@276359e7ce5d1097d4f3c57b143ca9a55507e527']],
                    u"doc":{
                        u"range": u"paul",
                        u'quantity': 2,
                        u"description": u"This is a very nice table",
                        u"design": u"office",
                        u"name": u"table",
                        u"version": [0, 2, 3],
                        u"options":{
                            u"configuration":{
                                u"color": [u"blue"],
                                u"size": [u"big"],
                                u"finish": [u"matt"]
                            },
                            u'manufacturing': {
                                u'material': [u'metal', u'wood'],
                                u'tool': [u'cnc']
                            }
                        }
                    }
                }

        product_flow.publish_context(self.db, json.dumps(context_dict))
        quantified_configuration = product_flow.get_quantified_configuration(self.db, json.dumps(choice_json), [u"context/uk_production_context"], 2)
        self.maxDiff = None
        self.assertEqual(quantified_configuration.get_json(), expected)


class TestFindingFilesets(unittest.TestCase):


    def setUp(self):
        self.db = MockKVStore()
        self.table = product_flow.publish_product(self.db, json.dumps(BASE_PRODUCT))

        CHAIR_PRODUCT =  {u"range": u"paul",
                    u"design": u"office",
                    u"name": u"chair",
                    u"version": [0, 2, 3],
                    u"description": u"This is a very nice table",
                    u"options":{
                        u"configuration":{
                            u"color": [u"red", u"green", u"blue"],
                            u"size": [u"big", u"small"]
                        },
                        u"manufacturing":{
                            u"tool": [u"cnc", u"laser"],
                            u"material": [u"wood", u"metal", u"plastic"]
                        }
                    }
                }

        self.chair = product_flow.publish_product(self.db, json.dumps(CHAIR_PRODUCT))

        fileset_dict_1 = {u"name": u"ply",
                    u"product": u"product/paul/office/table",
                    u"description": u"how to make table from ply",
                    u"files": [{u"file_one.txt": u"a_file_hash"}, {u"file_two.txt": u"a_file_hash"}],
                    u"options":{
                        u"configuration":{
                            u"color": [u"red", u"green", u"blue"],
                            u"size": u"big"
                        },
                        u"manufacturing":{
                            u"tool": u"cnc",
                            u"material": u"wood"
                        }
                    }
        }

        fileset_dict_2 = {u"name": u"ply",
                    u"product": u"product/paul/office/table",
                    u"description": u"how to make table from ply",
                    u"files": [{u"file_one.txt": u"a_file_hash"}, {u"file_two.txt": u"a_file_hash"}],
                    u"options":{
                        u"configuration":{
                            u"color": [u"red", u"green", u"blue"],
                            u"size": u"big"
                        },
                        u"manufacturing":{
                            u"tool": u"cnc",
                            u"material": u"metal"
                        }
                    }
        }

        fileset_dict_3 = {u"name": u"ply",
                    u"product": u"product/paul/office/table",
                    u"description": u"how to make table from ply",
                    u"files": [{u"file_one.txt": u"a_file_hash"}, {u"file_two.txt": u"a_file_hash"}],
                    u"quantity": 2,
                    u"options":{
                        u"configuration":{
                            u"color": [u"red", u"green", u"blue"],
                            u"size": u"big"
                        },
                        u"manufacturing":{
                            u"tool": u"cnc",
                            u"material": [u"wood"]
                        }
                    }
        }

        fileset_dict_4 = {u"name": u"ply",
                    u"product": u"product/paul/office/chair",
                    u"description": u"how to make table from ply",
                    u"files": [{u"file_one.txt": u"a_file_hash"}, {u"file_two.txt": u"a_file_hash"}],
                    u"options":{
                        u"configuration":{
                            u"color": [u"red", u"green", u"blue"],
                            u"size": u"big"
                        },
                        u"manufacturing":{
                            u"tool": u"cnc",
                            u"material": u"metal"
                        }
                    }
        }

        product_flow.publish_fileset(self.db, json.dumps(fileset_dict_1))
        product_flow.publish_fileset(self.db, json.dumps(fileset_dict_2))
        product_flow.publish_fileset(self.db, json.dumps(fileset_dict_3))
        product_flow.publish_fileset(self.db, json.dumps(fileset_dict_4))


    def test_get_filesets(self):

        possible_filesets = self.table.all_canonical_filesets(self.db)
        self.assertEqual(len(possible_filesets), 3)
        possible_filesets = self.chair.all_canonical_filesets(self.db)
        self.assertEqual(len(possible_filesets), 1)


    def test_get_filesets(self):

        quantified_config_json = {u"type": u"product",
                    u'created': get_timestamp(),
                    u'uri': u'product/paul/office/table@9756c7d2a375f786754e96f6baca4ddbbd550f82',
                    u'snapshot': True,
                    u'history': [[u'start', u'product/paul/office/table@e1fc779995c82d9fe65c18008709b2929d799517'],
                                 [u'merge', u'product/paul/office/table@8251cfaa2f86fbd798a9f8e21a1fb72f4d1db7dd'],
                                [u'merge', u'context/uk_production_context@276359e7ce5d1097d4f3c57b143ca9a55507e527']],
                    u"doc":{
                        u"range": u"paul",
                        u'quantity': 2,
                        u"description": u"This is a very nice table",
                        u"design": u"office",
                        u"name": u"table",
                        u"version": [0, 2, 3],
                        u"options":{
                            u"configuration":{
                                u"color": [u"blue"],
                                u"size": [u"big"],
                                u"finish": [u"matt"]
                            },
                            u'manufacturing': {
                                u'material': [u'metal', u'wood'],
                                u'tool': [u'cnc']
                            }
                        }
                    }
                }

        quantified_config = ProductSieve.from_json(json.dumps(quantified_config_json))
        quantified_config.save(self.db)

        found = product_flow.find_file_sets(self.db, u'product/paul/office/table@9756c7d2a375f786754e96f6baca4ddbbd550f82', [])

        self.assertEqual(len(found), 3)

        context_dict1 = {u"name": u"metal_only",
                    u"description": u"make things from metal",
                    u"options":{
                        u"manufacturing":{
                            u"material": u"metal"
                        }
                    }
        }

        context_dict2 = {u"name": u"wood_only",
                    u"description": u"make things from wood",
                    u"options":{
                      u"manufacturing":{
                            u"material": u"wood"
                        }
                    }
        }

        product_flow.publish_context(self.db, json.dumps(context_dict1))
        product_flow.publish_context(self.db, json.dumps(context_dict2))

        found = product_flow.find_file_sets(self.db, u'product/paul/office/table@9756c7d2a375f786754e96f6baca4ddbbd550f82', [u"context/wood_only"])
        self.assertEqual(len(found), 2)

        found = product_flow.find_file_sets(self.db, u'product/paul/office/table@9756c7d2a375f786754e96f6baca4ddbbd550f82', [u"context/metal_only"])
        self.assertEqual(len(found), 1)

"""

move doc into its own dict in the json
do doc hashing

"""