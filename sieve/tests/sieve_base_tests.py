import unittest
from sieve.sieve import Sieve
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


class TestValidSieve(unittest.TestCase):


    def test_valid_sieve(self):

        Sieve(BASE_PRODUCT)

        broken_option = deepcopy(BASE_PRODUCT)
        broken_option[u"options"][u"configuration"] = u"text"

        self.assertRaises(ProductExceptionFailedValidation, Sieve, broken_option)

        broken_option = deepcopy(BASE_PRODUCT)
        broken_option[u"options"] = u"text"

        self.assertRaises(ProductExceptionFailedValidation, Sieve, broken_option)

        broken_option = deepcopy(BASE_PRODUCT)
        broken_option[u"options"] = u"text"

        self.assertRaises(ProductExceptionFailedValidation, Sieve, broken_option)



class TestSieveAllows(unittest.TestCase):


    def setUp(self):
        self.base_sieve = Sieve(BASE_PRODUCT)


    def test_allows_subset(self):

        configured_option = deepcopy(BASE_PRODUCT)
        configured_option[u"options"][u"configuration"][u"color"] = u"red"
        configured_sieve = Sieve(configured_option)

        self.assertTrue(self.base_sieve.allows(configured_sieve))

        configured_option = deepcopy(BASE_PRODUCT)
        configured_option[u"options"][u"configuration"][u"color"] = [u"red", u"green"]
        configured_sieve = Sieve(configured_option)

        self.assertTrue(self.base_sieve.allows(configured_sieve))

        configured_option = deepcopy(BASE_PRODUCT)
        configured_option[u"options"][u"configuration"][u"color"] = [u"red", u"green"]
        configured_option[u"options"][u"manufacturing"][u"tool"] = [u"cnc"]
        configured_sieve = Sieve(configured_option)

        self.assertTrue(self.base_sieve.allows(configured_sieve))


    def test_allows_subset_without_a_key(self):

        configured_option = deepcopy(BASE_PRODUCT)
        del configured_option[u"options"][u"configuration"][u"color"]
        configured_sieve = Sieve(configured_option)
        self.assertTrue(self.base_sieve.allows(configured_sieve))


    def test_allows_subset_without_an_optionset(self):

        configured_option = deepcopy(BASE_PRODUCT)
        del configured_option[u"options"][u"configuration"]
        configured_sieve = Sieve(configured_option)
        self.assertTrue(self.base_sieve.allows(configured_sieve))


    def test_allows_subset_with_an_extra_key(self):

        configured_option = deepcopy(BASE_PRODUCT)
        configured_option[u"options"][u"configuration"][u"wheels"] = [u"big", u"small"]
        configured_sieve = Sieve(configured_option)
        self.assertTrue(self.base_sieve.allows(configured_sieve))


    def test_allows_fails(self):

        configured_option = deepcopy(BASE_PRODUCT)
        configured_option[u"options"][u"configuration"][u"color"] = u"purple"
        configured_sieve = Sieve(configured_option)
        self.assertFalse(self.base_sieve.allows(configured_sieve))


class TestSieveMerge(unittest.TestCase):


    def setUp(self):
        self.base_sieve = Sieve(BASE_PRODUCT)


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

        other_sieve = Sieve(other_dict)
        merged = self.base_sieve.merge(other_sieve)
        self.maxDiff = None
        self.assertEqual(merged.doc, expected)




class TestSieveExtract(unittest.TestCase):

    def setUp(self):
        self.base_sieve = Sieve(BASE_PRODUCT)


    def test_can_extract(self):

        expected =  {u"name": u"table",
                    u"description": u"This is a very nice table",
                    u"options":{
                        u"configuration":{
                            u"color": [u"red", u"green", u"blue"],
                            u"size": [u"big", u"small"]
                        }
                    }
                }

        extracted = self.base_sieve.extract([u"configuration"])
        self.maxDiff = None
        self.assertEqual(extracted.get_json(), expected)



class TestSievePatch(unittest.TestCase):

    def setUp(self):
        self.base_sieve = Sieve(BASE_PRODUCT)


    def test_does_a_patch(self):

        first_dict =  {u"name": u"something",
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

        expected =  {u"name": u"something",
                    u"description": u"these are other options",
                    u"options":{
                        u"configuration":{
                            u"color": [u"red", u"green", u"blue"],
                            u"size": [u"big", u"medium", u"small"]
                        },
                        u"manufacturing":{
                            u"tool": [u"cnc", u"laser", u"plaster"],
                            "material": [u"wood", u"metal", u"plastic"],
                            u"days": [u"tuesday", u"thursday"]
                        },
                        u"refreshments":{
                            u"drinks": [u"beer", u"coffee"],
                            u"snacks": [u"crisps", u"cheese", u"apple"]
                        }
                    }
                }

        first_sieve = Sieve(first_dict)
        patched = first_sieve.patch(self.base_sieve)
        self.maxDiff = None
        self.assertEqual(patched.get_json(), expected)


    def test_match(self):

        configured_product_1 = {u"name": u"cat",
                   u"description": u"This is a very nice table",
                   u"options":{
                        u"configuration":{
                            u"color": u"red",
                            u"size": u"big"
                        },
                   }
        }


        configured_product_2 = {u"name": u"dog",
                   u"description": u"This is a very nice table",
                   u"options":{
                        u"configuration":{
                            u"color": u"red",
                        },
                   }
        }


        configured_product_3 = {u"name": u"fish",
                   u"description": u"This is a very nice table",
                   u"options":{
                        u"configuration":{
                            u"color": u"red",
                            u"size": u"old"
                        },
                   }
        }

        configured_product_4 = {u"name": u"goat",
                   u"description": u"This is a very nice table",
                   u"options":{
                        u"configuration":{
                            u"color": [u"red", u"green"],
                            u"size": u"small"
                        },
                   }
        }


        found = self.base_sieve.match([Sieve(configured_product_1),
                                       Sieve(configured_product_2),
                                       Sieve(configured_product_3),
                                       Sieve(configured_product_4)])


        self.assertEqual(set([f.name for f in found]), set([u'cat', u'dog', u'goat']))


class TestSieveHistory(unittest.TestCase):


    def setUp(self):
        self.base_sieve = Sieve(BASE_PRODUCT)


    def test_does_a_patch(self):

        first_dict =  {u"name": u"something",
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

        expected =  {u"name": u"something",
                    u"description": u"these are other options",
                    u"options":{
                        u"configuration":{
                            u"color": [u"red", u"green", u"blue"],
                            u"size": [u"big", u"medium", u"small"]
                        },
                        u"manufacturing":{
                            u"tool": [u"cnc", u"laser", u"plaster"],
                            "material": [u"wood", u"metal", u"plastic"],
                            u"days": [u"tuesday", u"thursday"]
                        },
                        u"refreshments":{
                            u"drinks": [u"beer", u"coffee"],
                            u"snacks": [u"crisps", u"cheese", u"apple"]
                        }
                    }
                }

        first_sieve = Sieve(first_dict)
        patched = first_sieve.patch(self.base_sieve)
        self.maxDiff = None
        self.assertEqual(patched.doc, expected)



"""
References
expand_refs
strip_refs
"""