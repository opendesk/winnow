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

    def test_numeric(self):

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
            return "size: %i in %f seconds" % (max,(t2 - t1))

        print doit(Decimal('100'))
        print doit(Decimal('1000'))
        print doit(Decimal('10000'))
