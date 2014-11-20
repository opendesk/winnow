import os
import unittest
import json
from sieve.product_sieve import ProductSieve
from sieve.fileset_sieve import FilesetSieve
from sieve.context_sieve import ContextSieve
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
            u"description": u"This is a very nice table",
            u"design": u"office",
            u"frozen_uri": u"product/paul/office/table/frozen/88cbec9cd1a84d193c98e8dbd989d250",
            u"history": [u"start::product/paul/office/table@xxxxxxxx::0::2::3"],
            u"name": u"table",
            u"options": {
                u"configuration": {
                    u"color": [u"red", u"green", u"blue"],
                    u"size": [u"big", u"small"]
                },
                u"manufacturing": {
                    u"material": [u"wood", u"metal", u"plastic"],
                    u"tool": [u"cnc", u"laser"]
                }
            },
            u"range": u"paul",
            u"type": u"product",
            u"uri": u"product/paul/office/table",
            u"version": [0, 2, 3]
        }

        doc = json.dumps(BASE_PRODUCT)

        product_flow.publish_product(self.db, doc)

        fetched_doc = self.db.get("product/paul/office/table")
        fetched = ProductSieve(json.loads(fetched_doc))

        self.assertEqual(fetched.json_dict, expected)

        print json.dumps(fetched.json_dict, sort_keys=True, indent=4)










class TestPublishingFilesets(unittest.TestCase):


    def setUp(self):
        self.db = MockKVStore()
        product_flow.publish_product(self.db, json.dumps(BASE_PRODUCT))


    def test_publish_fileset_with_files(self):

        fileset_dict = {u"name": u"ply",
                    u"product": u"product/paul/office/table",
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

        cad_files = {u"file_one.txt": u"some text in files one",
                 u"file_two.txt": u"text in file two",
        }

        expected = {u"name": u"ply",
                    u"product": u'product/paul/office/table',
                    u"product_frozen": u'product/paul/office/table/frozen/88cbec9cd1a84d193c98e8dbd989d250',
                    u'product_history': [u'start::product/paul/office/table@xxxxxxxx::0::2::3'],
                    u"files": [u"fileset/paul/office/table/ply/file_one.txt", u"fileset/paul/office/table/ply/file_two.txt"],
                    u"description": u"how to make table from ply",
                    u'created': get_timestamp(),
                    u"uri": u"fileset/paul/office/table/ply/ply",
                    u'frozen_uri': u'fileset/paul/office/table/ply/ply/frozen/13c477751ee97a894e3747bf207bb618',
                    u'history': [u'start::fileset/paul/office/table/ply/ply@xxxxxxxx'],
                    u"type": u"fileset",
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

        fileset_json = json.dumps(fileset_dict)
        product_flow.publish_fileset(self.db, fileset_json, cad_files=cad_files)
        fetched_text = self.db.get(u"fileset/paul/office/table/ply/file_one.txt")
        self.assertEqual(fetched_text, u"some text in files one")

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

        expected = {u"range": u"paul",
                    u"design": u"office",
                    u"type": u"product",
                    u"name": u"table",
                    u'created': get_timestamp(),
                    u'uri': u'product/paul/office/table',
                    u'frozen_uri': u'product/paul/office/table/frozen/48a99e0565c51f9d1c88c39f1445767a',
                    u'history': [u'start::product/paul/office/table@xxxxxxxx::0::2::3', u'merge::context/uk_production_context@xxxxxxxx'],
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

        product_flow.publish_context(self.db, json.dumps(context_dict))
        config = product_flow.get_contextualised_product(self.db, u"product/paul/office/table", [u"context/uk_production_context"])
        self.maxDiff = None
        self.assertEqual(config.json_dict, expected)


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

        expected = {u"range": u"paul",
                    u"design": u"office",
                    u"type": u"product",
                    u"name": u"table",
                    u'created': get_timestamp(),
                    u'uri': u'product/paul/office/table',
                    u'frozen_uri': u'product/paul/office/table/frozen/4d8538c0b21e8a1baeb295eef7a97153',
                    u"version": [0, 2, 3],
                    u"description": u"This is a very nice table",
                    u'history': [u'start::product/paul/office/table@xxxxxxxx::0::2::3',
                                u'merge::context/uk_production_context@xxxxxxxx',
                                u'extract::configuration'],
                    u"options":{
                        u"configuration":{
                            u"color": [u"blue", u"green"],
                            u"size": [u"big"],
                            u"finish": [u"shiney", u"matt"]
                        }
                    }
                }


        product_flow.publish_context(self.db, json.dumps(context_dict))
        config = product_flow.get_contextualised_product(self.db, u"product/paul/office/table", [u"context/uk_production_context"], extractions=[u"configuration"])
        self.maxDiff = None
        self.assertEqual(config.json_dict, expected)
#
#
#     def test_get_contextualised_many(self):
#
#         context_dict1 = {u"name": u"uk_production_context",
#                     u"description": u"things that are possible in the uk",
#                     u"options":{
#                         u"configuration":{
#                             u"color": [u"green", u"blue", u"purple", u"orange"],
#                             u"size": u"big",
#                             u"finish": [u"shiney", u"matt"]
#                         },
#                         u"manufacturing":{
#                             u"tool": [u"cnc", u"casting"],
#                             u"material": [u"wood", u"metal"]
#                         }
#                     }
#         }
#
#         context_dict2 = {u"name": u"tue_production_context",
#                     u"description": u"things that are possible on tuesdays",
#                     u"options":{
#                         u"configuration":{
#                             u"color": [u"green", u"red"],
#                             u"finish": [u"shiney", u"matt", u"sandblasted"]
#                         },
#                         u"delivery":{
#                             u"days": [u"monday", u"tuesday", u"wednesday"],
#                             u"method": [u"hand", u"post"]
#                         }
#                     }
#         }
#
#         expected = {u"range": u"paul",
#                     u"design": u"office",
#                     u"type": u"product",
#                     u"name": u"table",
#                     u'created': get_timestamp(),
#                     u'uri': u'product/paul/office/table/frozen/92e252f5a7012fbea941ea76c1c2b06d',
#                     u"version": [0, 2, 3],
#                     u"description": u"This is a very nice table",
#                     u'ancestors': [[u"product/paul/office/table", [0, 2, 3]]],
#                     u'contexts': [u'context/uk_production_context', u'context/tue_production_context'],
#                     u"options":{
#                         u"configuration":{
#                             u"color": [u"green"],
#                             u"size": [u"big"],
#                             u"finish": [u"matt", u"shiney"]
#                         },
#                        u"manufacturing":{
#                             u"tool": [u"cnc"],
#                             u"material": [u"metal", u"wood"]
#                         },
#                         u"delivery":{
#                             u"days": [u"monday", u"tuesday", u"wednesday"],
#                             u"method": [u"hand", u"post"]
#                         }
#                     }
#                 }
#
#
#         product_flow.publish_context(self.db, json.dumps(context_dict1))
#         product_flow.publish_context(self.db, json.dumps(context_dict2))
#
#         config = product_flow.get_contextualised_product(self.db,
#                                                          u"product/paul/office/table",
#                                                          [u"context/uk_production_context", u"context/tue_production_context"])
#         self.maxDiff = None
#         self.assertEqual(config.json_dict, expected)
#
#
#
#
#
#     def test_fail_impossible_merge(self):
#
#         context_dict1 = {u"name": u"uk_production_context",
#                     u"description": u"things that are possible in the uk",
#                     u"options":{
#                         u"configuration":{
#                             u"color": [u"green", u"blue", u"purple", u"orange"],
#                             u"size": u"big",
#                             u"finish": [u"shiney", u"matt"]
#                         },
#                         u"manufacturing":{
#                             u"tool": [u"cnc", u"casting"],
#                             u"material": [u"wood", u"metal"]
#                         }
#                     }
#         }
#
#         context_dict2 = {u"name": u"tue_production_context",
#                     u"description": u"things that are possible on tuesdays",
#                     u"options":{
#                         u"configuration":{
#                             u"color": [u"red", u"pink"],
#                             u"finish": [u"shiney", u"matt", u"sandblasted"]
#                         },
#                         u"delivery":{
#                             u"days": [u"monday", u"tuesday", u"wednesday"],
#                             u"method": [u"hand", u"post"]
#                         }
#                     }
#         }
#
#         expected = {u"range": u"paul",
#                     u"design": u"office",
#                     u"type": u"product",
#                     u"name": u"table",
#                     u'created': get_timestamp(),
#                     u'uri': u'product/paul/office/table/frozen/92e252f5a7012fbea941ea76c1c2b06d',
#                     u"version": [0, 2, 3],
#                     u"description": u"This is a very nice table",
#                     u'ancestors': [[u"product/paul/office/table", [0, 2, 3]]],
#                     u'contexts': [u'context/uk_production_context', u'context/tue_production_context'],
#                     u"options":{
#                         u"configuration":{
#                             u"color": [u"green"],
#                             u"size": [u"big"],
#                             u"finish": [u"matt", u"shiney"]
#                         },
#                        u"manufacturing":{
#                             u"tool": [u"cnc"],
#                             u"material": [u"metal", u"wood"]
#                         },
#                         u"delivery":{
#                             u"days": [u"monday", u"tuesday", u"wednesday"],
#                             u"method": [u"hand", u"post"]
#                         }
#                     }
#                 }
#
#
#         product_flow.publish_context(self.db, json.dumps(context_dict1))
#         product_flow.publish_context(self.db, json.dumps(context_dict2))
#
#         self.assertRaises(ProductExceptionEmptyOptionValues,
#                           product_flow.get_contextualised_product,
#                           self.db,
#                           u"product/paul/office/table",
#                           [u"context/uk_production_context", u"context/tue_production_context"])
#
#
