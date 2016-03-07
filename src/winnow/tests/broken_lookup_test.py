

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


size_1 = {
    u"name": u"Sizes",
    u"scopes": [
        u"customer"
    ],
    u"type": u"set::string",
    u"values": [
        {
            u"description": u"",
            u"length": 2400.0,
            u"name": u"915x2400",
            u"type": u"string",
            u"units": u"mm",
            u"value": u"915x2400",
            u"width": 915.0
        }
    ]
}

size_2 = {
    u"default": u"915x2400",
    u"description": u"Choose product size",
    u"name": u"Sizes",
    u"scopes": [
        u"customer"
    ],
    u"type": u"set::string",
    u"values": [
        {
            u"description": u"",
            u"length": 1600.0,
            u"name": u"915x1600",
            u"type": u"string",
            u"units": u"mm",
            u"value": u"915x1600",
            u"width": 915.0
        },
        {
            u"description": u"",
            u"length": 1800.0,
            u"name": u"915x1800",
            u"type": u"string",
            u"units": u"mm",
            u"value": u"915x1800",
            u"width": 915.0
        },
        {
            u"description": u"",
            u"length": 2000.0,
            u"name": u"915x2000",
            u"type": u"string",
            u"units": u"mm",
            u"value": u"915x2000",
            u"width": 915.0
        },
        {
            u"description": u"",
            u"length": 2200.0,
            u"name": u"915x2200",
            u"type": u"string",
            u"units": u"mm",
            u"value": u"915x2200",
            u"width": 915.0
        },
        {
            u"description": u"",
            u"length": 2250.0,
            u"name": u"915x2250",
            u"type": u"string",
            u"units": u"mm",
            u"value": u"915x2250",
            u"width": 915.0
        },
        {
            u"description": u"",
            u"length": 2400.0,
            u"name": u"915x2400",
            u"type": u"string",
            u"units": u"mm",
            u"value": u"915x2400",
            u"width": 915.0
        }
    ]
}



class TestDisallowedkeys(unittest.TestCase):


    def setUp(self):
        self.db = MockKVStore()


    def test_disallowed(self):


        SIZE_2 = {u"name": u"table",
                    u"description": u"This is a very nice table",
                    u"options":{
                        u"size": size_2,
                    }
                }

        SIZE_1 = {u"name": u"choice",
                    u"options":{
                        u"size": size_1,
                    }
                }

        table = WinnowVersion.add_doc(self.db, SIZE_2, {})
        choice = WinnowVersion.add_doc(self.db, SIZE_1, {})

        disallowed = winnow.disallowed_keys(choice, table)

        print disallowed

        self.assertEqual(len(disallowed), 0)