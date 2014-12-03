import time
import unittest
from sieve.sieve import PublishedSieve, get_doc_hash
from db import MockKVStore


BASE_PRODUCT =  {u"name": u"table",
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


class TestSieveMerge(unittest.TestCase):


    def setUp(self):
        self.base_sieve = PublishedSieve(BASE_PRODUCT)


    def test_does_a_merge(self):

        other_dict =  {u"name": u"something",
                            u"description": u"these are other options",
                            u"options":{
                                u"configuration":{
                                    u"color": [u"red", u"blue"],
                                    u"size": [u"big", u"medium", u"small"]
                                },
                                u"manufacturing":{
                                    u"tool": [u"cnc", u"laser", u"plaster"],
                                    u"days": [u"tuesday", u"thursday"]
                                },
                                u"refreshments":{
                                    u"drinks": [u"beer", u"coffee"],
                                    u"snacks": [u"crisps", u"cheese", u"apple"]
                                }
                            }
                        }

        expected =  {   u"type": u"base",
                        u"created": get_timestamp(),
                        u'history': [[u'start', u'base/table@38e442718dc0a0b4e9aa582042f306216e32702b'],
                                    [u"merge", u"base/something@449ac0e21b41ce3fdf2f85275053aef74c567609"]],
                        u'uri': u'base/table@97de1a2dba3dc684718e5aea5973556f628abf2b',
                        u"doc": {u"name": u"table",
                            u"description": u"This is a very nice table",
                            u"options":{
                                u"configuration":{
                                    u"color": [u"blue", u"red"],
                                    u"size": [u"big", u"small"]
                                },
                                u"manufacturing":{
                                    u"tool": [u"cnc", u"laser"],
                                    u"material": [u"wood", u"metal", u"plastic"],
                                    u"days": [u"tuesday", u"thursday"]
                                },
                                u"refreshments":{
                                    u"drinks": [u"beer", u"coffee"],
                                    u"snacks": [u"crisps", u"cheese", u"apple"]
                                }
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
                    u'history': [[u'start', u'base/table@38e442718dc0a0b4e9aa582042f306216e32702b'],
                                 [u"extract", [u"configuration"]]],
                    u'uri': u'base/table@d3ce02d05b69bf0a1dbac911c6ded63a47aecdbd',
                    u"doc":{
                    u"name": u"table",
                        u"description": u"This is a very nice table",
                        u"options":{
                            u"configuration":{
                                u"color": [u"red", u"green", u"blue"],
                                u"size": [u"big", u"small"]
                            }
                        }
                    }
                }

        extracted = self.base_sieve.extract([u"configuration"])
        self.maxDiff = None
        self.assertEqual(extracted.get_json(), expected)



class TestSievePatch(unittest.TestCase):

    def setUp(self):
        self.base_sieve = PublishedSieve(BASE_PRODUCT)


    def test_does_a_patch(self):

        target_dict =  {u"name": u"something",
                            u"description": u"these are other options",
                            u"options":{
                                u"configuration":{
                                    u"size": [u"big", u"medium", u"small"]
                                },
                                u"manufacturing":{
                                    u"tool": [u"cnc", u"laser", u"plaster"],
                                    u"days": [u"tuesday", u"thursday"]
                                },
                                u"refreshments":{
                                    u"drinks": [u"beer", u"coffee"],
                                    u"snacks": [u"crisps", u"cheese", u"apple"]
                                }
                            }
                        }

        expected =  {
                    u"type": u"base",
                    u"created": get_timestamp(),
                    u'history': [[u'start', u'base/table@38e442718dc0a0b4e9aa582042f306216e32702b'],
                                 [u"patch", u"base/something@4bcd2904e906c8ce7d75cc9135ff24520ac58686"]],
                    u'uri': u'base/table@653e4d6134309239cbb3dcc29b13a473f94b3cff',
                    u"doc":{
                        u"name": u"table",
                        u"description": u"This is a very nice table",
                        u"options":{
                            u"configuration":{
                                u"color": [u"red", u"green", u"blue"],
                                u"size": [u"big", u"small"]
                            },
                            u"manufacturing":{
                                u"tool": [u"cnc", u"laser"],
                                u"material": [u"wood", u"metal", u"plastic"],
                                u"days": [u"tuesday", u"thursday"]
                            },
                            u"refreshments":{
                                u"drinks": [u"beer", u"coffee"],
                                u"snacks": [u"crisps", u"cheese", u"apple"]
                            }
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


        self.base_sieve = PublishedSieve(BASE_PRODUCT_UPSTREAM)


    def test_can_freeze(self):

        parent_dict =  {u"name": u"parent",
                            u"description": u"these are other options",
                            u"options":{
                                u"configuration":{
                                    u"size": [u"big", u"medium", u"small"]
                                },
                                u"manufacturing":{
                                    u"tool": [u"cnc", u"laser", u"plaster"],
                                    u"days": [u"tuesday", u"thursday"]
                                },
                                u"refreshments":{
                                    u"drinks": [u"beer", u"coffee"],
                                    u"snacks": [u"crisps", u"cheese", u"apple"]
                                }
                            }
                        }

        expected =  {
                    u"type": u"base",
                    u"created": get_timestamp(),
                    u'history': [[u'start', u'base/table@99e9c3de9c2d038ba9bfd4d084ecc83ab9cf6941'],
                                 [u"patch", u"base/parent@15f81687d6b2c3b1b579004c7b421bae56a1a7f9"]],
                    u"snapshot": True,
                    u'uri': u'base/table@bb7b97465584fc9110bfd8d76ff7ab50fd087ee9',
                    u"doc":{
                        u"name": u"table",
                        u'upstream': u'base/parent',
                        u"description": u"This is a very nice table",
                        u"options":{
                            u"configuration":{
                                u"color": [u"red", u"green", u"blue"],
                                u"size": [u"big", u"small"]
                            },
                            u"manufacturing":{
                                u"tool": [u"cnc", u"laser"],
                                u"material": [u"wood", u"metal", u"plastic"],
                                u"days": [u"tuesday", u"thursday"]
                            },
                            u"refreshments":{
                                u"drinks": [u"beer", u"coffee"],
                                u"snacks": [u"crisps", u"cheese", u"apple"]
                            }
                        }
                    }
                }

        parent_sieve = PublishedSieve(parent_dict)
        self.assertEqual(parent_sieve.uri, u'base/parent@15f81687d6b2c3b1b579004c7b421bae56a1a7f9')
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
                                u"configuration":{
                                    u"size": [u"big", u"medium", u"small"]
                                },
                                u"manufacturing":{
                                    u"tool": [u"cnc", u"laser", u"plaster"],
                                    u"days": [u"tuesday", u"thursday"]
                                },
                                u"refreshments":{
                                    u"drinks": [u"beer", u"coffee"],
                                    u"snacks": [u"crisps", u"cheese", u"apple"]
                                }
                            }
                        }

        parent_dict =  {u"name": u"parent",
                        u"upstream": u"base/grandad",
                            u"description": u"these are other options",
                            u"options":{
                                u"configuration":{
                                    u"size": [u"big", u"medium", u"small"]
                                },
                                u"manufacturing":{
                                    u"tool": [u"cnc", u"laser", u"plaster"],
                                },
                                u"refreshments":{
                                    u"drinks": [u"beer", u"coffee", u"water"],
                                }
                            }
                        }

        expected =  {
                    u"type": u"base",
                    u"created": get_timestamp(),
                    u'history': [[u'start', u'base/table@99e9c3de9c2d038ba9bfd4d084ecc83ab9cf6941'],
                                 [u"patch", u"base/parent@b39dd06a049cfc8093ae947eeadc661bb82f7d0c"],
                                 [u"patch", u"base/grandad@1fe4aae68135113f73177de5b24e6636f227cdcd"]],
                    u'uri': u'base/table@180929557c8fcc897eb941cd36a6356690c67db7',
                    u'snapshot': True,
                    u"doc":{
                        u"name": u"table",
                        u"description": u"This is a very nice table",
                        u'upstream': u'base/parent',
                        u"options":{
                            u"configuration":{
                                u"color": [u"red", u"green", u"blue"],
                                u"size": [u"big", u"small"]
                            },
                            u"manufacturing":{
                                u"tool": [u"cnc", u"laser"],
                                u"material": [u"wood", u"metal", u"plastic"],
                                u"days": [u"tuesday", u"thursday"]
                            },
                            u"refreshments":{
                                u"drinks": [u"beer", u"coffee", u"water"],
                                u"snacks": [u"crisps", u"cheese", u"apple"]
                            }
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