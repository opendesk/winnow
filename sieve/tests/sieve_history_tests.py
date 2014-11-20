import time
import unittest
from sieve.sieve import Sieve, PublishedSieve
from db import MockKVStore
from copy import deepcopy
from sieve.product_exceptions import ProductExceptionFailedValidation, ProductExceptionNoAllowed


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

        expected =  {u"name": u"table",
                    u"description": u"This is a very nice table",
                    u"type": u"base",
                    u"created": get_timestamp(),
                    u'history': [u'start::base/table@xxxxxxxx',
                                 u"merge::base/something@xxxxxxxx"],
                    u'uri': u'base/table',
                    u'frozen_uri': u'base/table/frozen/b310f7a96c3bb677365f67a6566f5920',
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

        other_sieve = PublishedSieve(other_dict)
        merged = self.base_sieve.merge(other_sieve)
        self.maxDiff = None
        self.assertEqual(merged.json_dict, expected)




class TestSieveExtract(unittest.TestCase):

    def setUp(self):
        self.base_sieve = PublishedSieve(BASE_PRODUCT)


    def test_can_extract(self):

        expected =  {u"name": u"table",
                    u"description": u"This is a very nice table",
                    u"type": u"base",
                    u"created": get_timestamp(),
                    u'frozen_uri': u'base/table/frozen/e9b7a16e453a35fe51089ab58cd465b0',
                    u'history': [u'start::base/table@xxxxxxxx', u'extract::configuration'],
                    u'uri': u'base/table',
                    u"options":{
                        u"configuration":{
                            u"color": [u"red", u"green", u"blue"],
                            u"size": [u"big", u"small"]
                        }
                    }
                }

        extracted = self.base_sieve.extract([u"configuration"])
        self.maxDiff = None
        self.assertEqual(extracted.json_dict, expected)



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

        expected =  {u"name": u"table",
                    u"description": u"This is a very nice table",
                    u"type": u"base",
                    u"created": get_timestamp(),
                    u'history': [u"start::base/table@xxxxxxxx",
                                 u"patch::base/something@xxxxxxxx"],
                    u'uri': u'base/table',
                    u'frozen_uri': u'base/table/frozen/4d80780f965658d1bf7c320b83d38d04',
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

        target_sieve = PublishedSieve(target_dict)
        patched = self.base_sieve.patch(target_sieve)
        self.maxDiff = None
        self.assertEqual(patched.json_dict, expected)



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

        expected =  {u"name": u"table",
                    u"description": u"This is a very nice table",
                    u"type": u"base",
                    u"created": get_timestamp(),
                    u'history': [u'start::base/table@xxxxxxxx', u'patch::base/parent@xxxxxxxx'],
                    u'uri': u'base/table',
                    u'frozen_uri': u'base/table/frozen/48ea3138ebabcfe9c98ca693085acd74',
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


        parent_sieve = PublishedSieve(parent_dict)
        parent_sieve.save(self.db)

        patched = self.base_sieve.patch_upstream(self.db)
        self.maxDiff = None
        self.assertEqual(patched.json_dict, expected)


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

        expected =  {u"name": u"table",
                    u"description": u"This is a very nice table",
                    u"type": u"base",
                    u"created": get_timestamp(),
                    u'history': [u"start::base/table@xxxxxxxx",
                                 u"patch::base/parent@xxxxxxxx",
                                 u"patch::base/grandad@xxxxxxxx",],
                    u'uri': u'base/table',
                    u'frozen_uri': u'base/table/frozen/43604a0fcb4a31da698384492a2da636',
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


        parent_sieve = PublishedSieve(parent_dict)
        parent_sieve.save(self.db)

        grand_parent_sieve = PublishedSieve(grand_parent_dict)
        grand_parent_sieve.save(self.db)

        patched = self.base_sieve.patch_upstream(self.db)
        self.maxDiff = None
        self.assertEqual(patched.json_dict, expected)

"""
References
expand_refs
strip_refs
"""