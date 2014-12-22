import time
import unittest
from sieve.base_sieve import PublishedSieve, get_doc_hash
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

def get_timestamp():
    return unicode(time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()))


class TestSieveMerge(unittest.TestCase):


    def setUp(self):
        self.base_sieve = PublishedSieve(BASE_PRODUCT)


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

        expected =  {   u"type": u"base",
                        u"created": get_timestamp(),
                        u'history': [[u'start', u'base/table@14ce7c80b1563e38bdbf1ce33f4d07603dfc8520'],
                                    [u"merge", u"base/something@82d5cad60480369715f597dc454aa6d897cf3cba"]],
                        u'uri': u'base/table@33b082d1ad3506af8f937644f887c16a01b5d22e',
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

        other_sieve = PublishedSieve(other_dict)
        merged = self.base_sieve.merge(other_sieve)
        self.maxDiff = None
        self.assertEqual(merged.get_json(), expected)




class TestSieveExtract(unittest.TestCase):

    def setUp(self):
        self.base_sieve = PublishedSieve(BASE_PRODUCT)


    def test_can_extract(self):

        expected =  {
                    u"type": u"base",
                    u"created": get_timestamp(),
                    u'history': [[u'start', u'base/table@14ce7c80b1563e38bdbf1ce33f4d07603dfc8520'],
                                 [u"extract", [u"color", u"size"]]],
                    u'uri': u'base/table@8c4e3238ac1c6d53167e9cb3c924a67ed670b086',
                    u"doc":{
                    u"name": u"table",
                        u"description": u"This is a very nice table",
                        u"options":{
                            u"color": [u"red", u"green", u"blue"],
                            u"size": [u"big", u"small"]
                        }
                    }
                }

        extracted = self.base_sieve.extract([u"color", u"size"])
        self.maxDiff = None
        self.assertEqual(extracted.get_json(), expected)



class TestSievePatch(unittest.TestCase):

    def setUp(self):
        self.base_sieve = PublishedSieve(BASE_PRODUCT)


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
                    u"type": u"base",
                    u"created": get_timestamp(),
                    u'history': [[u'start', u'base/table@14ce7c80b1563e38bdbf1ce33f4d07603dfc8520'],
                                 [u"patch", u"base/something@b4fa6c27c2c634d61c472e92b4bc5744a77dc497"]],
                    u'uri': u'base/table@ea9cf5c3936a6b4086b7d5640b61b2d2024cc822',
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

        target_sieve = PublishedSieve(target_dict)
        patched = self.base_sieve.patch(target_sieve)
        self.maxDiff = None
        self.assertEqual(patched.get_json(), expected)



class TestSieveFreeze(unittest.TestCase):

    def setUp(self):

        self.db = MockKVStore()

        BASE_PRODUCT_UPSTREAM =  {u"name": u"table",
                    u"description": u"This is a very nice table",
                    u"upstream": u"base/parent",
                    u"options":{
                        u"color": [u"red", u"green", u"blue"],
                        u"size": [u"big", u"small"],
                        u"tool": [u"cnc", u"laser"],
                        u"material": [u"wood", u"metal", u"plastic"]
                    }
                }


        self.base_sieve = PublishedSieve(BASE_PRODUCT_UPSTREAM)


    def test_can_freeze(self):

        parent_dict =  {u"name": u"parent",
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
                    u"type": u"base",
                    u"created": get_timestamp(),
                    u'history': [[u'start', u'base/table@61ad825071616ba1f9cb959196ba558cbf6f46d1'],
                                 [u"patch", u"base/parent@55ad519e41c4ce8e4c9fad7cc91d04696fc923e2"]],
                    u"snapshot": True,
                    u'uri': u'base/table@caacb9427005986c386acbe1fbbeebbe5c98e7f4',
                    u"doc":{
                        u"name": u"table",
                        u'upstream': u'base/parent',
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

        parent_sieve = PublishedSieve(parent_dict)
        self.assertEqual(parent_sieve.uri, u'base/parent@55ad519e41c4ce8e4c9fad7cc91d04696fc923e2')
        parent_sieve.save(self.db, index=u"base/parent")
        upstream_json = self.db.get(u"base/parent")
        upstream_sieve = PublishedSieve.from_json(upstream_json)
        self.assertEqual(parent_sieve.uri, upstream_sieve.uri)
        snapshot = self.base_sieve.take_snapshot(self.db)
        self.maxDiff = None
        self.assertEqual(snapshot.get_json(), expected)


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
                        u"upstream": u"base/grandad",
                            u"description": u"these are other options",
                            u"options":{
                                u"size": [u"big", u"medium", u"small"],
                                u"tool": [u"cnc", u"laser", u"plaster"],
                                u"drinks": [u"beer", u"coffee", u"water"],
                            }
                        }

        expected =  {
                    u"type": u"base",
                    u"created": get_timestamp(),
                    u'history': [[u'start', u'base/table@61ad825071616ba1f9cb959196ba558cbf6f46d1'],
                                 [u"patch", u"base/parent@bf9c06ec14be8538051045fb0295c962788f59cc"],
                                 [u"patch", u"base/grandad@8b7f701e5f0d13551a4b7ccfb62259c5c9f68517"]],
                    u'uri': u'base/table@d2489b834bc5c963777c0911cb12d70ace2790e5',
                    u'snapshot': True,
                    u"doc":{
                        u"name": u"table",
                        u"description": u"This is a very nice table",
                        u'upstream': u'base/parent',
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


        parent_sieve = PublishedSieve(parent_dict)
        parent_sieve.save(self.db, index=u"base/parent")

        grand_parent_sieve = PublishedSieve(grand_parent_dict)
        grand_parent_sieve.save(self.db, index=u"base/grandad")

        snapshot = self.base_sieve.take_snapshot(self.db)
        self.maxDiff = None
        self.assertEqual(snapshot.get_json(), expected)


class TestGitHash(unittest.TestCase):

    def test_git_hashing(self):
        content = "elephant poo\n"
        desired_hash2 = u"a447f047ae30ce4a2b994efdff3691b6b5e53603"
        produced_hash = get_doc_hash(content)
        self.assertEqual(desired_hash2, produced_hash)





"""
References
expand_refs
strip_refs
"""