from decimal import Decimal
from numeric_values import NumericNumberWinnowValue, NumericWinnowValue
from option_values import OptionWinnowValue, OptionNullWinnowValue
from boolean_values import BooleanWinnowValue
from winnow.constants import *



def value_with_key(value, key):

    key_parts = key.split("/")

    if len(key_parts) == 1:
        return value
    else:
        opt = key_parts[-1]
        new_value = {
            u"type": VALUE_TYPE_SET_NULL,
            u"options": {
                opt: value
            }
        }
        new_key = "/".join(key_parts[:-1])

        return value_with_key(new_value, new_key)


def value_factory(input_value, key=None):

    value = input_value if key is None else value_with_key(input_value, key)

    cls = None

    if isinstance(value, dict):
        cls = VALUE_TYPES[value["type"]]
    elif  isinstance(value, bool):
        cls = BooleanWinnowValue

    elif isinstance(value, int) or isinstance(value, Decimal)or isinstance(value, float):
        cls = NumericWinnowValue

    elif isinstance(value, unicode):
        cls = OptionWinnowValue

    elif value is None:
        cls = OptionNullWinnowValue

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
    VALUE_TYPE_SET_COLOUR: OptionWinnowValue,
    VALUE_TYPE_SET_SIZE: OptionWinnowValue,
    VALUE_TYPE_SET_RESOURCE: OptionWinnowValue,
    VALUE_TYPE_SET_NULL: OptionNullWinnowValue
}