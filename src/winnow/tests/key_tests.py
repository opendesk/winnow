import unittest
from decimal import Decimal

from winnow.constants import *
from winnow.utils import json_dumps

from winnow.keys.key_matching import KeyMatcher

NESTED_OPTIONS = {
            u"type": VALUE_TYPE_SET_STRING,
            u"name": u"colour",
            u"description": u"please choose one of the colours",
            VALUES_KEY_NAME: [
                {
                    u"type": VALUE_TYPE_SET_STRING,
                    u"name": u"red",
                    u"description": u"the colour red",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"red",
                    u"options":{
                        u"paint_coats":{
                            u"type": VALUE_TYPE_NUMERIC_STEP,
                            u"max": Decimal(6),
                            u"min": Decimal(1),
                            u"start": Decimal(1),
                            u"step": Decimal(1),
                        }
                    }
                },
                {
                    u"type": VALUE_TYPE_SET_STRING,
                    u"name": u"blue",
                    u"description": u"the colour blue",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"blue"
                }
            ]
        }


class  TestbrokenMatcher(unittest.TestCase):

    def test_finish_matcher(self):

        options_dict_b =  {
            u"configuration": u"straight-tops",
            u"material-choices": {
                u"default": u"standard-laminate",
                u"name": u"Material",
                u"type": u"set::string",
                u"values": {
                    u"name": u"Standard Laminate",
                    u"options": {
                        u"finish": u"$ref:/finishes/opendesk/standard-laminate"
                    },
                    u"type": u"string",
                    u"value": u"standard-laminate"
                }
            }
        }

        b_matcher = KeyMatcher.from_dict(options_dict_b)

        self.assertEqual(b_matcher.options["material-choices/finish"], "$ref:/finishes/opendesk/standard-laminate")




class TestNestedKeyMatcher(unittest.TestCase):

    def test_nested_key_matcher(self):

        matcher = KeyMatcher()
        matcher.add_options(NESTED_OPTIONS, "piggy")
        self.assertEqual(matcher.options.keys(), [u'piggy/paint_coats', u'piggy'])

        self.assertEqual(matcher.get(u'piggy/paint_coats'), {
                            u"type": VALUE_TYPE_NUMERIC_STEP,
                            u"max": Decimal(6),
                            u"min": Decimal(1),
                            u"start": Decimal(1),
                            u"step": Decimal(1),
                        })


class TestKeyMatcher(unittest.TestCase):

    def test_key_matcher(self):

        matcher = KeyMatcher()

        self.assertTrue(matcher.validate("paul"))
        self.assertTrue(matcher.validate("piggy/paint_coats"))
        self.assertTrue(matcher.validate("paul/bum"))
        self.assertTrue(matcher.validate("paul/bum/head"))
        self.assertTrue(matcher.validate("*/paul"))

        self.assertFalse(matcher.validate("paul/"))
        self.assertFalse(matcher.validate("paul/bum/"))
        self.assertFalse(matcher.validate("/paul"))
        self.assertFalse(matcher.validate("paul/*/head"))
        self.assertFalse(matcher.validate("/*/paul"))

    def test_key_matcher_get(self):
        matcher = KeyMatcher()
        matcher.set("paul", "test")
        self.assertEqual(matcher.get("paul"), "test")

    def test_key_matcher_get_fail(self):
        matcher = KeyMatcher()
        matcher.set("paul", "test")
        self.assertEqual(matcher.get("pauls"), None)

    def test_key_matcher_get_2(self):
        matcher = KeyMatcher()
        matcher.set("paul", "test")
        self.assertEqual(matcher.get("*/paul"), "test")

    def test_key_matcher_get_3(self):
        matcher = KeyMatcher()
        matcher.set("*/paul", "test")
        self.assertEqual(matcher.get("*/paul"), "test")

    def test_key_matcher_get_4(self):
        matcher = KeyMatcher()
        matcher.set("*/paul", "test")
        self.assertEqual(matcher.get("paul"), "test")

    def test_key_matcher_get_5(self):
        matcher = KeyMatcher()
        matcher.set("any/thing/else/paul", "test")
        self.assertEqual(matcher.get("paul"), None)

    def test_key_matcher_get_6(self):
        matcher = KeyMatcher()
        matcher.set("any/thing/else/paul", "test")
        self.assertEqual(matcher.get("*/paul"), "test")

    def test_key_matcher_get_7(self):
        matcher = KeyMatcher()
        matcher.set("*/paul", "test")
        self.assertEqual(matcher.get("any/thing/else/paul"), "test")