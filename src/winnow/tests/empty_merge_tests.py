import unittest
import winnow
from winnow.models.base import WinnowVersion
import json

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


class TestMergeCreatesExceptionValue(unittest.TestCase):


    def setUp(self):
        self.db = MockKVStore()
        self.base_version = WinnowVersion.add_doc(self.db, BASE_PRODUCT, {})

    def test_does_a_merge(self):

        other_dict =  {u"name": u"something",
                        u"description": u"these are other options",
                        u"options":{
                            u"color": [u"red", u"blue"],
                            u"size": [u"medium"],
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
                        u"material": [u"metal", u"plastic", u"wood"],
                        u"days": [u"thursday", u"tuesday"],
                        u"drinks": [u"beer", u"coffee"],
                        u"snacks": [u"apple", u"cheese", u"crisps"]
                    }
                }

        other_version =  WinnowVersion.add_doc(self.db, other_dict, {})
        merged = WinnowVersion.merged(self.db, BASE_PRODUCT, {}, self.base_version, other_version)

        size = merged.get_doc()["options"]["size"]

        self.assertTrue(isinstance(size, dict))
        self.assertEqual(size["type"],"exception")
        self.assertEqual(size["values"], [[u'big', u'small'], u'medium'])

        self.assertTrue("errors" in merged.get_doc())

        print json.dumps(merged.get_doc()["errors"], indent=4)

        expected_error = [
    [
        {
            "values": [
                [
                    "big",
                    "small"
                ],
                "medium"
            ],
            "type": "exception",
            "context": {
                "source_b": {
                    "description": "these are other options",
                    "options": {
                        "snacks": [
                            "crisps",
                            "cheese",
                            "apple"
                        ],
                        "color": [
                            "red",
                            "blue"
                        ],
                        "tool": [
                            "cnc",
                            "laser",
                            "plaster"
                        ],
                        "days": [
                            "tuesday",
                            "thursday"
                        ],
                        "drinks": [
                            "beer",
                            "coffee"
                        ],
                        "size": [
                            "medium"
                        ]
                    },
                    "name": "something"
                },
                "source_a": {
                    "description": "This is a very nice table",
                    "options": {
                        "color": [
                            "red",
                            "green",
                            "blue"
                        ],
                        "tool": [
                            "cnc",
                            "laser"
                        ],
                        "material": [
                            "wood",
                            "metal",
                            "plastic"
                        ],
                        "size": [
                            "big",
                            "small"
                        ]
                    },
                    "name": "table"
                }
            },
            "key": "size"
        }
    ]
]
        # print "errors: ", merged.get_doc()["errors"]

        # self.assertEqual(merged.get_doc()["errors"], expected_error)




    def test_can_merge_exception (self):

        other_dict =  {u"name": u"something",
                        u"description": u"these are other options",
                        u"options":{
                            u"color": [u"red", u"blue"],
                            u"size": [u"medium"],
                            u"tool": [u"cnc", u"laser", u"plaster"],
                            u"days": [u"tuesday", u"thursday"],
                            u"drinks": [u"beer", u"coffee"],
                            u"snacks": [u"crisps", u"cheese", u"apple"]
                        }
                    }

        third_dict =  {u"name": u"elephant",
                        u"description": u"another bunch of stuff",
                        u"options":{
                            u"color": [u"red", u"blue"],
                            u"size": [u"small"],
                            u"coffee": [u"latte", u"piccolo"]
                        }
                    }

        expected =  {u"name": u"table",
                    u"description": u"This is a very nice table",
                    u"options":{
                        u"color": [u"blue", u"red"],
                        u"size": [u"big", u"small"],
                        u"tool": [u"cnc", u"laser"],
                        u"material": [u"metal", u"plastic", u"wood"],
                        u"days": [u"thursday", u"tuesday"],
                        u"drinks": [u"beer", u"coffee"],
                        u"snacks": [u"apple", u"cheese", u"crisps"]
                    }
                }

        other_version =  WinnowVersion.add_doc(self.db, other_dict, {})
        merged_version = WinnowVersion.merged(self.db, BASE_PRODUCT, {}, self.base_version, other_version)
        third_version =  WinnowVersion.add_doc(self.db, third_dict, {})
        merged_again = WinnowVersion.merged(self.db, merged_version.get_doc(), {}, merged_version, third_version)
        size = merged_again.get_doc()["options"]["size"]

        self.assertTrue(isinstance(size, dict))
        self.assertEqual(size["type"],"exception")
        self.assertEqual(size["values"], [[u'big', u'small'], u'medium'])





    def test_default(self):

        other_dict =  {u"name": u"something",
                        u"description": u"these are other options",
                        u"options":{
                            u"color": [u"red", u"blue"],
                            u"size": [u"medium"],
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
                        u"material": [u"metal", u"plastic", u"wood"],
                        u"days": [u"thursday", u"tuesday"],
                        u"drinks": [u"beer", u"coffee"],
                        u"snacks": [u"apple", u"cheese", u"crisps"]
                    }
                }

        other_version =  WinnowVersion.add_doc(self.db, other_dict, {})
        merged_version = WinnowVersion.merged(self.db, BASE_PRODUCT, {}, self.base_version, other_version)


        default = winnow.default_choices(merged_version, [])

