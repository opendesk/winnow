import unittest
import decimal

from winnow.utils import json_loads, json_dumps, to_decimal, from_decimal

class TestJsonEncoding(unittest.TestCase):






    def test_roundtrip_floats(self):

        v = "2.2"

        as_python_float = json_loads(v)

        self.assertTrue(isinstance(as_python_float, float))

        as_decimal = to_decimal(as_python_float)

        self.assertTrue(isinstance(as_decimal, decimal.Decimal))
        self.assertEqual(decimal.Decimal("2.2"), as_decimal)
        self.assertEqual("2.2", json_dumps(json_loads(v)))

        v = "2.2639520464"

        as_python_float = json_loads(v)

        self.assertTrue(isinstance(as_python_float, float))

        as_decimal = to_decimal(as_python_float)

        self.assertTrue(isinstance(as_decimal, decimal.Decimal))
        self.assertEqual(decimal.Decimal(v), as_decimal)
        self.assertEqual(v, json_dumps(json_loads(v)))
