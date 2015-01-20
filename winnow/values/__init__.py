from decimal import Decimal
from numeric_sieve_values import NumericNumberSieveValue, NumericSieveValue
from option_sieve_values import OptionSieveValue
from sieve.constants import *


def value_factory(value):

    if isinstance(value, dict):
        return VALUE_TYPES[value["type"]].from_value(value)

    if isinstance(value, int) or isinstance(value, Decimal)or isinstance(value, float):
        return NumericSieveValue.from_value(value)

    if isinstance(value, list):
        v = value[0]

        if isinstance(v, int) or isinstance(v, Decimal)or isinstance(v, float):
            return NumericSieveValue.from_value(value)
        if isinstance(v, unicode):
            return OptionSieveValue.from_value(value)

    if isinstance(value, unicode):
        return OptionSieveValue.from_value(value)

    return None



VALUE_TYPES = {
    VALUE_TYPE_NUMERIC_RANGE: NumericSieveValue,
    VALUE_TYPE_NUMERIC_NUMBER: NumericSieveValue,
    VALUE_TYPE_NUMERIC_SET: NumericSieveValue,
    VALUE_TYPE_NUMERIC_STEP: NumericSieveValue,
    VALUE_TYPE_OPTION_STRING: OptionSieveValue,

}