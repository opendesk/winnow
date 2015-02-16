import unittest
from decimal import Decimal

from winnow.values import value_factory
from winnow.values.option_values import OptionSieveValue, OptionStringSieveValue
from winnow.constants import *

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

        self.assertTrue(isinstance(option, OptionStringSieveValue))
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

        self.assertTrue(isinstance(intersection, OptionStringSieveValue))
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
                            u"value": [u"cox", u"jazz", u"bramley"]
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

        self.assertTrue(isinstance(intersection, OptionStringSieveValue))
        self.assertTrue(isinstance(d, dict))
        self.assertTrue(d[VALUES_KEY_NAME][1][u"value"] == u"red")
        self.assertTrue(d[VALUES_KEY_NAME][1][u"options"][u"paint_coats"][u"max"] == Decimal(6))
        self.assertTrue(d[VALUES_KEY_NAME][1][u"options"][u"apples"][u"value"] == [u"cox", u"jazz", u"bramley"])

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

        self.assertTrue(isinstance(intersection, OptionStringSieveValue))
        self.assertTrue(isinstance(d, dict))
        self.assertTrue(d[VALUES_KEY_NAME][1][u"value"] == u"red")
        self.assertTrue(d[VALUES_KEY_NAME][1][u"options"][u"paint_coats"][u"max"] == Decimal(6))

        ## the other way round
        intersection = option4.intersection(option1)
        d = intersection.as_json()

        self.assertTrue(isinstance(intersection, OptionStringSieveValue))
        self.assertTrue(isinstance(d, dict))
        self.assertTrue(d[VALUES_KEY_NAME][1][u"value"] == u"red")
        self.assertTrue(d[VALUES_KEY_NAME][1][u"options"][u"paint_coats"][u"max"] == Decimal(6))


    def test_isdisjoint(self):
        """
        disjoint is unaffected by nested options. I think.

        """