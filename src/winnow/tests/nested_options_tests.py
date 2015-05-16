import unittest
from decimal import Decimal

from winnow.values import value_factory
from winnow.values.option_values import OptionWinnowValue, OptionStringWinnowValue
from winnow.constants import *
from winnow.options import OptionsSet
from winnow.utils import json_dumps

from winnow.exceptions import OptionsExceptionFailedValidation, OptionsExceptionIncompatibleTypes

NESTED_OPTIONS_STRING = {
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


class TestNestedOptionSieveCreation(unittest.TestCase):


    def test_create_proper_string_single(self):

        option = value_factory(NESTED_OPTIONS_STRING)

        d = option.as_json()

        self.assertTrue(isinstance(option, OptionStringWinnowValue))
        self.assertEqual(option.type, VALUE_TYPE_SET_STRING)
        self.assertTrue(isinstance(d, dict))

        self.assertEqual(len(option), 2)


    def test_is_subset(self):
        """
        should just work the same
        but needs to check is subset of matching child options
        """

        NESTED_OPTIONS_STRING_2 = {
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
                            u"max": 6,
                            u"min": 1,
                            u"start": 1,
                            u"step": 1,
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

        option1 = value_factory(NESTED_OPTIONS_STRING)
        option2 = value_factory(NESTED_OPTIONS_STRING_2)

        # same is subset
        self.assertTrue(option1.issubset(option2))


        NESTED_OPTIONS_STRING_3 = {
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
                            u"max": 4,
                            u"min": 2,
                            u"start": 1,
                            u"step": 1,
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

        NESTED_OPTIONS_STRING_4 = {
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
                            u"max": 12,
                            u"min": 2,
                            u"start": 1,
                            u"step": 1,
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

        option3 = value_factory(NESTED_OPTIONS_STRING_3)
        option4 = value_factory(NESTED_OPTIONS_STRING_4)


        # less is subset
        self.assertTrue(option3.issubset(option1))

        # more is not subset
        self.assertFalse(option4.issubset(option1))


    def test_intersection(self):
        """
        if there are matching values both with options then their options are merged

        """


        NESTED_OPTIONS_STRING_2 = {
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
                            u"max": Decimal(8),
                            u"min": Decimal(4),
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

        option1 = value_factory(NESTED_OPTIONS_STRING)
        option2 = value_factory(NESTED_OPTIONS_STRING_2)

        intersection = option1.intersection(option2)
        d = intersection.as_json()

        self.assertTrue(isinstance(intersection, OptionStringWinnowValue))
        self.assertTrue(isinstance(d, dict))
        self.assertTrue(d[VALUES_KEY_NAME][1][u"value"] == u"red")
        self.assertTrue(set(d[VALUES_KEY_NAME][1][u"options"][u"paint_coats"][u"value"]) == {Decimal(4), Decimal(5), Decimal(6)})

        ## if they have different keys check merge ok

        NESTED_OPTIONS_STRING_3 = {
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
                        u"apples":{
                            u"type": VALUE_TYPE_SET_STRING,
                            u"values": [u"cox", u"jazz", u"bramley"]
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


        option3 = value_factory(NESTED_OPTIONS_STRING_3)

        intersection = option1.intersection(option3)
        d = intersection.as_json()

        self.assertTrue(isinstance(intersection, OptionStringWinnowValue))
        self.assertTrue(isinstance(d, dict))
        self.assertTrue(d[VALUES_KEY_NAME][1][u"value"] == u"red")
        self.assertTrue(d[VALUES_KEY_NAME][1][u"options"][u"paint_coats"][u"max"] == Decimal(6))
        options = d[VALUES_KEY_NAME][1][u"options"]
        self.assertTrue(options[u"apples"] == [u"cox", u"jazz", u"bramley"])

    def test_intersection_2(self):
        ## if have no options just copies

        NESTED_OPTIONS_STRING_4 = {
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

        option1 = value_factory(NESTED_OPTIONS_STRING)
        option4 = value_factory(NESTED_OPTIONS_STRING_4)

        intersection = option1.intersection(option4)
        d = intersection.as_json()

        self.assertTrue(isinstance(intersection, OptionStringWinnowValue))
        self.assertTrue(isinstance(d, dict))
        self.assertTrue(d[VALUES_KEY_NAME][1][u"value"] == u"red")
        self.assertTrue(d[VALUES_KEY_NAME][1][u"options"][u"paint_coats"][u"max"] == Decimal(6))

        ## the other way round
        intersection = option4.intersection(option1)
        d = intersection.as_json()

        self.assertTrue(isinstance(intersection, OptionStringWinnowValue))
        self.assertTrue(isinstance(d, dict))
        self.assertTrue(d[VALUES_KEY_NAME][1][u"value"] == u"red")
        self.assertTrue(d[VALUES_KEY_NAME][1][u"options"][u"paint_coats"][u"max"] == Decimal(6))


    def test_isdisjoint(self):
        """
        disjoint is unaffected by nested options. I think.

        """




class TestNestedOptionWithNulls(unittest.TestCase):

    def test_null(self):


        options_1 = {
            u"colour": {
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
                            u"apples":{
                                u"type": VALUE_TYPE_SET_STRING,
                                u"values": [u"cox", u"jazz", u"bramley"]
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
        }

        options_2 = {
            u"colour/apples": [u"cox", u"jazz"]
        }

        set1 = OptionsSet(options_1)
        set2 = OptionsSet(options_2)

        merged = set1.merge(set2).store

        expected = {
            "colour": {
                "default": "blue",
                "description": "please choose one of the colours",
                "name": "colour",
                "type": "set::string",
                "values": [
                    {
                        "description": "the colour blue",
                        "image_uri": "http://something.com/khgfdkyg.png",
                        "name": "blue",
                        "type": "set::string",
                        "value": "blue"
                    },
                    {
                        "description": "the colour red",
                        "image_uri": "http://something.com/khgfdkyg.png",
                        "name": "red",
                        "options": {
                            "apples": [
                                "cox",
                                "jazz"
                            ]
                        },
                        "type": "set::string",
                        "value": "red"
                    }
                ]
            }
        }

        self.assertEqual(expected, merged)


class TestWildCards(unittest.TestCase):


    def test_wildcard(self):

        options_1 = {
            u"colour": {
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
                            u"apples":{
                                u"type": VALUE_TYPE_SET_STRING,
                                u"values": [u"cox", u"jazz", u"bramley"]
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
        }

        options_2 = {
            u"*/apples": [u"cox", u"jazz"]
        }

        set1 = OptionsSet(options_1)
        set2 = OptionsSet(options_2)

        self.assertEqual(set1.matcher.options.keys(), [u"colour", u"colour/apples"])
        self.assertEqual(set2.matcher.options.keys(), [u"*/apples"])

        mega_store_1 = set1.mega_store(set2)
        mega_store_2 = set2.mega_store(set1)

        self.assertEqual(mega_store_1.keys(), [u"colour"])

        merged = set1.merge(set2).store

        expected = [
            {
                "description": "the colour blue",
                "image_uri": "http://something.com/khgfdkyg.png",
                "name": "blue",
                "type": "set::string",
                "value": "blue"
            },
            {
                "description": "the colour red",
                "image_uri": "http://something.com/khgfdkyg.png",
                "name": "red",
                "options": {
                    "apples": [
                        "cox",
                        "jazz"
                    ]
                },
                "type": "set::string",
                "value": "red"
            }
        ]

        self.assertEqual(expected, merged["colour"]["values"])



