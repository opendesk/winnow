import unittest
from winnow.values import value_factory
from winnow.values.boolean_values import BooleanWinnowValue
from winnow.constants import *

from winnow.exceptions import OptionsExceptionFailedValidation, OptionsExceptionIncompatibleTypes



class TestNumberSieveCreation(unittest.TestCase):

    def test_convienence_methods_single_values(self):

        b = value_factory(True)
        value = b.as_json()

        self.assertTrue(isinstance(b, BooleanWinnowValue))
        self.assertEqual(value[u"type"], VALUE_TYPE_BOOLEAN)
        self.assertTrue(isinstance(value[u"value"], bool))
        self.assertEqual(value[u"value"], True)

        b = value_factory(False)
        value = b.as_json()

        self.assertTrue(isinstance(b, BooleanWinnowValue))
        self.assertEqual(value[u"type"], VALUE_TYPE_BOOLEAN)
        self.assertTrue(isinstance(value[u"value"], bool))
        self.assertEqual(value[u"value"], False)

        b = value_factory([False, True])
        value = b.as_json()

        self.assertTrue(isinstance(b, BooleanWinnowValue))
        self.assertEqual(value[u"type"], VALUE_TYPE_BOOLEAN)
        self.assertTrue(isinstance(value[u"value"], list))
        self.assertEqual(value[u"value"], [True, False])


    def test_convienence_methods_single_values_fail(self):
        self.assertRaises(OptionsExceptionFailedValidation, value_factory, [True, 2])
        self.assertRaises(OptionsExceptionFailedValidation, value_factory, [True, True])
        self.assertRaises(OptionsExceptionFailedValidation, value_factory, [True, True, False])
        self.assertRaises(OptionsExceptionFailedValidation, value_factory, [True, False, 4])

    def test_creation(self):

        doc = {
            "type": "boolean",
            "value": True
        }

        b = value_factory(doc)
        value = b.as_json()

        self.assertTrue(isinstance(b, BooleanWinnowValue))
        self.assertEqual(value[u"type"], VALUE_TYPE_BOOLEAN)
        self.assertTrue(isinstance(value[u"value"], bool))
        self.assertEqual(value[u"value"], True)

        doc = {
            "type": "boolean",
            "value": False
        }

        b = value_factory(doc)
        value = b.as_json()

        self.assertTrue(isinstance(b, BooleanWinnowValue))
        self.assertEqual(value[u"type"], VALUE_TYPE_BOOLEAN)
        self.assertTrue(isinstance(value[u"value"], bool))
        self.assertEqual(value[u"value"], False)

        doc = {
            "type": "boolean",
            "value": [False, True]
        }

        b = value_factory(doc)
        value = b.as_json()

        self.assertTrue(isinstance(b, BooleanWinnowValue))
        self.assertEqual(value[u"type"], VALUE_TYPE_BOOLEAN)
        self.assertTrue(isinstance(value[u"value"], list))
        self.assertEqual(value[u"value"], [True, False])


    def test_subset(self):

        t = value_factory(True)
        f = value_factory(False)
        n = value_factory([False, True])
        n2 = value_factory([True, False])

        self.assertTrue(t.issubset(n))
        self.assertTrue(f.issubset(n))
        self.assertTrue(n2.issubset(n))
        self.assertFalse(n.issubset(t))
        self.assertFalse(n.issubset(f))
        self.assertFalse(t.issubset(f))
        self.assertFalse(f.issubset(t))


    def test_disjoint(self):

        t = value_factory(True)
        f = value_factory(False)
        n = value_factory([False, True])
        n2 = value_factory([True, False])

        self.assertFalse(t.isdisjoint(n))
        self.assertFalse(f.isdisjoint(n))
        self.assertFalse(n2.isdisjoint(n))
        self.assertFalse(n.isdisjoint(t))
        self.assertFalse(n.isdisjoint(f))
        self.assertTrue(t.isdisjoint(f))
        self.assertTrue(f.isdisjoint(t))

    def test_intersection(self):

        t = value_factory(True)
        f = value_factory(False)
        n = value_factory([False, True])
        n2 = value_factory([True, False])

        self.assertEqual(t.intersection(n).true, True)
        self.assertEqual(t.intersection(f), None)
        self.assertEqual(f.intersection(t), None)
        self.assertEqual(f.intersection(n).true, False)
        self.assertEqual(n.intersection(n2).true, None)