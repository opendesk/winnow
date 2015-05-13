import unittest


from winnow.values import value_factory
from winnow.values.option_values import OptionWinnowValue, OptionStringWinnowValue
from winnow.constants import *

from winnow.exceptions import OptionsExceptionFailedValidation, OptionsExceptionIncompatibleTypes


class TestResourceOptionCreation(unittest.TestCase):

    def test_convienence_methods_single_values(self):




        resource = value_factory(u"red")
        d = option.as_json()

