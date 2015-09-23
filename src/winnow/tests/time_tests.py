import time

from decimal import Decimal
from winnow.values import value_factory



import unittest
from decimal import Decimal

from winnow.values import value_factory
from winnow.values.numeric_values import NumericNumberWinnowValue, \
    NumericSetWinnowValue, \
    NumericRangeWinnowValue, \
    NumericStepWinnowValue
from winnow.constants import *

from winnow.exceptions import OptionsExceptionFailedValidation, OptionsExceptionIncompatibleTypes



class TestNumericTimings(unittest.TestCase):

    def test_numeric_step_timings(self):

        def doit(max):
            v = {
                'name': u'Quantity',
                'min': Decimal('1'),
                'default': Decimal('1'),
                'max': max,
                'start': Decimal('0'),
                'step': Decimal('1'),
                'type': u'numeric::step'
            }
            t1 = time.time()
            d = value_factory(v).default
            t2 = time.time()
            return (t2 - t1)


        dur = doit(Decimal('1000000000'))
        print dur
        self.assertTrue(dur < 0.005)


    def test_numeric_range_timings(self):

        def doit(max):
            v = {
                'name': u'Quantity',
                'min': Decimal('1'),
                'default': Decimal('1'),
                'max': max,
                'type': u'numeric::range'
            }
            t1 = time.time()
            d = value_factory(v).default
            t2 = time.time()
            return (t2 - t1)


        dur = doit(Decimal('1000000000'))
        self.assertTrue(dur < 0.005)


    def test_numeric_merge_timings(self):

        def doit(max):
            v1 = {
                'name': u'Quantity',
                'min': Decimal('1'),
                'default': Decimal('1'),
                'max': max,
                'start': Decimal('0'),
                'step': Decimal('1'),
                'type': u'numeric::step'
            }

            v2 = 1

            A = value_factory(v1)
            B = value_factory(v2)

            t1 = time.time()
            intersection = A.intersection(B)
            t2 = time.time()
            return (t2 - t1)


        dur = doit(Decimal('1000000000'))
        print dur
        self.assertTrue(dur < 0.005)