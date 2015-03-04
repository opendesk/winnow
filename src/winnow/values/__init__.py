from decimal import Decimal
from numeric_values import NumericNumberSieveValue, NumericWinnowValue
from option_values import OptionWinnowValue
from winnow.constants import *


def value_factory(value):

    if isinstance(value, dict):
        return VALUE_TYPES[value["type"]].from_value(value)

    if isinstance(value, int) or isinstance(value, Decimal)or isinstance(value, float):
        return NumericWinnowValue.from_value(value)

    if isinstance(value, list):
        v = value[0]

        if isinstance(v, int) or isinstance(v, Decimal)or isinstance(v, float):
            return NumericWinnowValue.from_value(value)
        if isinstance(v, unicode):
            return OptionWinnowValue.from_value(value)

    if isinstance(value, unicode):
        return OptionWinnowValue.from_value(value)

    return None


VALUE_TYPES = {
    VALUE_TYPE_NUMERIC_RANGE: NumericWinnowValue,
    VALUE_TYPE_NUMERIC_NUMBER: NumericWinnowValue,
    VALUE_TYPE_NUMERIC_SET: NumericWinnowValue,
    VALUE_TYPE_NUMERIC_STEP: NumericWinnowValue,
    VALUE_TYPE_SET_STRING: OptionWinnowValue,
    VALUE_TYPE_SET_RESOURCE: OptionWinnowValue
}