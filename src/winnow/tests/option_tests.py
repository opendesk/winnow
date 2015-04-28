import unittest
from decimal import Decimal

from winnow.values import value_factory
from winnow.values.option_values import OptionWinnowValue, OptionStringWinnowValue
from winnow.constants import *




from winnow.exceptions import OptionsExceptionFailedValidation, OptionsExceptionIncompatibleTypes

BASIC_STRING = {
            u"type": VALUE_TYPE_SET_STRING,
            u"name": u"colour",
            u"description": u"please choose one of the colours",
            u"default": "red",
            VALUES_KEY_NAME: [
                {
                    u"type": VALUE_TYPE_VALUE_STRING,
                    u"name": u"red",
                    u"description": u"the colour red",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"red",
                },
                {
                    u"type": VALUE_TYPE_VALUE_STRING,
                    u"name": u"blue",
                    u"description": u"the colour blue",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"blue"
                }
            ]
        }


class TestOptionSieveCreation(unittest.TestCase):

    def test_convienence_methods_single_values(self):

        option = value_factory(u"red")
        d = option.as_json()

        self.assertTrue(isinstance(option, OptionStringWinnowValue))
        self.assertEqual(option.type, VALUE_TYPE_SET_STRING)
        self.assertEqual(d, u"red")


    def test_convienence_methods_lists(self):

        option = value_factory([u"red", u"blue"])
        d = option.as_json()

        self.assertTrue(isinstance(option, OptionStringWinnowValue))
        self.assertEqual(d, [u"red", u"blue"])

        values = option.values

        self.assertTrue(isinstance(values, list))
        self.assertEqual(len(values), 2)
        self.assertTrue(isinstance(values[0], unicode))

        option = value_factory([u"red"])
        d = option.as_json()

        self.assertTrue(isinstance(option, OptionStringWinnowValue))
        self.assertEqual(d, u"red")


    def test_create_proper_string_single(self):

        option = value_factory({
            u"type": VALUE_TYPE_SET_STRING,
            u"name": u"red",
            u"description": u"the colour red", ## optional??
            VALUES_KEY_NAME: u"red"
        })

        d = option.as_json()

        self.assertTrue(isinstance(option, OptionStringWinnowValue))
        self.assertEqual(option.type, VALUE_TYPE_SET_STRING)
        self.assertTrue(isinstance(d, dict))
        self.assertEqual(d[VALUES_KEY_NAME], u"red")


    def test_create_proper_string_list(self):

        option = value_factory({
            u"type": VALUE_TYPE_SET_STRING,
            u"uri": u"colour/red",## optional
            u"name": u"red",
            u"description": u"the colour red", ## optional??
            u"image_uri": u"http://something.com/khgfdkyg.png",
            VALUES_KEY_NAME: [u"red", u"blue"]
        })

        d = option.as_json()

        self.assertTrue(isinstance(option, OptionStringWinnowValue))
        self.assertEqual(option.type, VALUE_TYPE_SET_STRING)
        self.assertTrue(isinstance(d, dict))
        self.assertEqual(d[VALUES_KEY_NAME], [u"red", u"blue"])


    def test_create_proper_string_proper_list(self):

        option = value_factory(BASIC_STRING)

        d = option.as_json()

        self.assertTrue(isinstance(option, OptionStringWinnowValue))
        self.assertEqual(option.type, VALUE_TYPE_SET_STRING)
        self.assertTrue(isinstance(d, dict))
        self.assertTrue(isinstance(d[VALUES_KEY_NAME], list))
        self.assertTrue(isinstance(d[VALUES_KEY_NAME][0], dict))
        self.assertEqual(d[VALUES_KEY_NAME][0]["value"], u"red")


    def test_is_subset(self):

        option1 = value_factory({
            u"type": VALUE_TYPE_SET_STRING,
            u"name": u"colour",
            u"description": u"please choose one of the colours",
            VALUES_KEY_NAME: [
                {
                    u"type": VALUE_TYPE_VALUE_STRING,
                    u"name": u"red",
                    u"description": u"the colour red",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"red",
                },
                {
                    u"type": VALUE_TYPE_VALUE_STRING,
                    u"name": u"blue",
                    u"description": u"the colour blue",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"blue"
                }
            ]
        })

        option2 = value_factory({
            u"type": VALUE_TYPE_SET_STRING,
            u"name": u"colour",
            u"description": u"please choose one of the colours",
            VALUES_KEY_NAME: [
                {
                    u"type": VALUE_TYPE_VALUE_STRING,
                    u"name": u"red",
                    u"description": u"the colour red",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"red",
                },
                {
                    u"type": VALUE_TYPE_VALUE_STRING,
                    u"name": u"blue",
                    u"description": u"the colour blue",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"blue"
                }
            ]
        })

        self.assertTrue(option1.issubset(option2))

        option3 = value_factory({
            u"type": VALUE_TYPE_SET_STRING,
            u"name": u"colour",
            u"description": u"please choose one of the colours",
            VALUES_KEY_NAME: [
                {
                    u"type": VALUE_TYPE_VALUE_STRING,
                    u"name": u"red",
                    u"description": u"the colour red",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"red",
                }
            ]
        })

        self.assertTrue(option3.issubset(option1))
        self.assertFalse(option1.issubset(option3))

        option4 = value_factory({
            u"type": VALUE_TYPE_SET_STRING,
            u"name": u"colour",
            u"description": u"please choose one of the colours",
            VALUES_KEY_NAME: [
                {
                    u"type": VALUE_TYPE_VALUE_STRING,
                    u"name": u"pink",
                    u"description": u"the colour red",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"red",
                }
            ]
        })

        self.assertTrue(option4.issubset(option1))

        option5 = value_factory({
            u"type": VALUE_TYPE_SET_STRING,
            u"name": u"colour",
            u"description": u"please choose one of the colours",
            VALUES_KEY_NAME: [
                {
                    u"type": VALUE_TYPE_VALUE_STRING,
                    u"name": u"pink",
                    u"description": u"the colour red",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"pink",
                }
            ]
        })

        self.assertFalse(option5.issubset(option1))


    def test_intersection(self):


        option1 = value_factory({
            u"type": VALUE_TYPE_SET_STRING,
            u"name": u"colour",
            u"description": u"please choose one of the colours",
            u"image_url": u"http://something.com/kurtjyrd.png",
            VALUES_KEY_NAME: [
                {
                    u"type": VALUE_TYPE_VALUE_STRING,
                    u"name": u"red",
                    u"description": u"the colour red",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"red",
                },
                {
                    u"type": VALUE_TYPE_VALUE_STRING,
                    u"name": u"blue",
                    u"description": u"the colour blue",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"blue"
                }
            ]
        })

        option2 = value_factory({
            u"type": VALUE_TYPE_SET_STRING,
            u"name": u"colour",
            u"description": u"please choose one of the colours",
            u"scopes": [u"client"],
            VALUES_KEY_NAME: [
                {
                    u"type": VALUE_TYPE_VALUE_STRING,
                    u"name": u"green",
                    u"description": u"the colour green",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"green",
                },
                {
                    u"type": VALUE_TYPE_VALUE_STRING,
                    u"name": u"blue 2",
                    u"description": u"the colour blue again",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"blue"
                }
            ]
        })

        option3 = option1.intersection(option2)



        d = option3.as_json()

        self.assertTrue(isinstance(option3, OptionStringWinnowValue))
        self.assertEqual(option3.type, VALUE_TYPE_SET_STRING)
        self.assertTrue(isinstance(d, dict))

        self.assertTrue(isinstance(d[VALUES_KEY_NAME], dict))
        self.assertEqual(d[VALUES_KEY_NAME]["value"], u"blue")
        self.assertEqual(d[VALUES_KEY_NAME]["name"], u"blue")
        self.assertEqual(d[VALUES_KEY_NAME]["description"], u"the colour blue")
        self.assertEqual(d[u"scopes"], [u"client"])
        self.assertEqual(d[u"image_url"], u"http://something.com/kurtjyrd.png")


        option8 = value_factory([u"green", u"blue"])
        option9 = option1.intersection(option8)
        d = option9.as_json()

        self.assertTrue(isinstance(option3, OptionStringWinnowValue))
        self.assertEqual(option3.type, VALUE_TYPE_SET_STRING)
        self.assertTrue(isinstance(d, dict))

        self.assertTrue(isinstance(d[VALUES_KEY_NAME], dict))
        self.assertEqual(d[VALUES_KEY_NAME]["value"], u"blue")
        self.assertEqual(d[VALUES_KEY_NAME]["name"], u"blue")
        self.assertEqual(d[VALUES_KEY_NAME]["description"], u"the colour blue")
        self.assertEqual(d[u"image_url"], u"http://something.com/kurtjyrd.png")


        option10 = option8.intersection(option1)
        d = option10.as_json()

        self.assertTrue(isinstance(option3, OptionStringWinnowValue))
        self.assertEqual(option3.type, VALUE_TYPE_SET_STRING)
        self.assertTrue(isinstance(d, dict))

        self.assertTrue(isinstance(d[VALUES_KEY_NAME], dict))
        self.assertEqual(d[VALUES_KEY_NAME]["value"], u"blue")
        self.assertEqual(d[VALUES_KEY_NAME]["name"], u"blue")
        self.assertEqual(d[VALUES_KEY_NAME]["description"], u"the colour blue")
        self.assertEqual(d[u"image_url"], u"http://something.com/kurtjyrd.png")


        option4 = value_factory({
            u"type": VALUE_TYPE_SET_STRING,
            u"name": u"colour",
            u"description": u"please choose one of the colours",
            VALUES_KEY_NAME: [
                {
                    u"type": VALUE_TYPE_VALUE_STRING,
                    u"name": u"red",
                    u"description": u"the colour red",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"red",
                },
                {
                    u"type": VALUE_TYPE_VALUE_STRING,
                    u"name": u"green",
                    u"description": u"the colour green",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"green",
                },
                {
                    u"type": VALUE_TYPE_VALUE_STRING,
                    u"name": u"blue",
                    u"description": u"the colour blue",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"blue"
                }
            ]
        })

        option5 = option1.intersection(option4)

        d = option5.as_json()

        self.assertTrue(isinstance(option5, OptionStringWinnowValue))
        self.assertEqual(option5.type, VALUE_TYPE_SET_STRING)
        self.assertEqual(len(option5), 2)
        self.assertTrue(isinstance(d, dict))
        self.assertTrue(isinstance(d[VALUES_KEY_NAME], list))
        self.assertTrue(isinstance(d[VALUES_KEY_NAME][0], dict))
        self.assertTrue(d[VALUES_KEY_NAME][0]["value"] in [u"red", u"blue"])
        self.assertTrue(d[VALUES_KEY_NAME][1]["value"] in [u"red", u"blue"])
        self.assertTrue(d[VALUES_KEY_NAME][0]["value"] !=  d[VALUES_KEY_NAME][1]["value"])

        option6 = value_factory({
            u"type": VALUE_TYPE_SET_STRING,
            u"name": u"colour",
            u"description": u"please choose one of the colours",
            VALUES_KEY_NAME: [
                {
                    u"type": VALUE_TYPE_VALUE_STRING,
                    u"name": u"green",
                    u"description": u"the colour green",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"green",
                },
                {
                    u"type": VALUE_TYPE_VALUE_STRING,
                    u"name": u"orange",
                    u"description": u"the colour orange",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"value": u"orange"
                }
            ]
        })

        option7 = option1.intersection(option6)

        self.assertTrue(option7 is None)


    def test_is_subset_with_path(self):

        option1 = value_factory({
            u"type": VALUE_TYPE_SET_RESOURCE,
            u"name": u"colour",
            u"description": u"please choose one of the colours",
            VALUES_KEY_NAME: [
                u"red",
            ]
        })

        option2 = value_factory({
            u"type": VALUE_TYPE_SET_RESOURCE,
            u"name": u"colour",
            u"description": u"please choose one of the colours",
            VALUES_KEY_NAME: [
                {
                    u"type": u"material",
                    u"name": u"red",
                    u"description": u"the colour red",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"path": u"red",
                },
                {
                    u"type": u"material",
                    u"name": u"blue",
                    u"description": u"the colour blue",
                    u"image_uri": u"http://something.com/khgfdkyg.png",
                    u"path": u"blue"
                }
            ]
        })

        self.assertTrue(option1.issubset(option2))


