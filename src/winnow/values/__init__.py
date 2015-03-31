from decimal import Decimal
from numeric_values import NumericNumberWinnowValue, NumericWinnowValue
from option_values import OptionWinnowValue
from boolean_values import BooleanWinnowValue
from winnow.constants import *


def value_factory(value):

    cls = None

    if isinstance(value, dict):
        cls = VALUE_TYPES[value["type"]]

    elif  isinstance(value, bool):
        cls = BooleanWinnowValue

    elif isinstance(value, int) or isinstance(value, Decimal)or isinstance(value, float):
        cls = NumericWinnowValue

    elif isinstance(value, unicode):
        cls = OptionWinnowValue

    elif isinstance(value, list):
        v = value[0]
        if isinstance(v, int) or isinstance(v, Decimal)or isinstance(v, float):
            cls = NumericWinnowValue
        if isinstance(v, unicode):
            cls = OptionWinnowValue
        if isinstance(v, bool):
            cls = BooleanWinnowValue
    else:
        pass

    if cls:
        return cls.from_value(value)

    return None


VALUE_TYPES = {
    VALUE_TYPE_BOOLEAN: BooleanWinnowValue,
    VALUE_TYPE_NUMERIC_RANGE: NumericWinnowValue,
    VALUE_TYPE_NUMERIC_NUMBER: NumericWinnowValue,
    VALUE_TYPE_NUMERIC_SET: NumericWinnowValue,
    VALUE_TYPE_NUMERIC_STEP: NumericWinnowValue,
    VALUE_TYPE_SET_STRING: OptionWinnowValue,
    VALUE_TYPE_SET_RESOURCE: OptionWinnowValue
}