import unittest
from decimal import Decimal

from winnow.values import value_factory
from winnow.values.option_values import OptionWinnowValue, OptionStringWinnowValue, OptionNullWinnowValue
from winnow.constants import *
from winnow.utils import json_dumps




from winnow.exceptions import OptionsExceptionFailedValidation, OptionsExceptionIncompatibleTypes

BASIC_STRING = {
            u"type": u"set:string",
            u"name": u"colour",
            u"description": u"please choose one of the colours",
            u"default": u"red",
            u"values": [
                {
                    u"type": u"string",
                    u"name": u"red",
                    u"description": u"the colour red",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"red",
                },
                {
                    u"type": u"string",
                    u"name": u"blue",
                    u"description": u"the colour blue",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"blue"
                }
            ]
        }





class TestOptionNullCreation(unittest.TestCase):

    def test_convienence_methods_none(self):

        option = value_factory(None)
        d = option.as_json()
        self.assertTrue(isinstance(option, OptionNullWinnowValue))
        self.assertEqual(option.type, VALUE_TYPE_SET_NULL)
        print d
        self.assertTrue(d is None)

    def test_logic(self):

        null_option = value_factory(None)

        string_option = value_factory([u"red", u"blue"])
        self.assertTrue(string_option.issubset(null_option))
        self.assertTrue(string_option.intersection(null_option) == string_option)
        self.assertTrue(string_option.isdisjoint(null_option) is False)


    def test_options_creation(self):

        NULL_STRING = {
            u"type": VALUE_TYPE_SET_NULL,
            u"options": {
                u"eat": [u"fish", u"chips"]
            }
        }

        null_option = value_factory(NULL_STRING)

        string_option = value_factory([u"red", u"green"])
        self.assertTrue(string_option.issubset(null_option))

        intersection = string_option.intersection(null_option)

        expected = [{'type': u'string', 'value': u'green'}, {'type': u'string', 'value': u'red'}]

        self.assertEqual(expected, intersection.as_json())
        self.assertTrue(string_option.isdisjoint(null_option) is False)