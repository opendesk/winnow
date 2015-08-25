
"""
NumericSieveValue

normally always created using the from_value method in the base class

the value input can be:

- convienence versions

an int

a float

a Decimal

a list of ints, floats or decimals

- proper versions

{type: "numeric::range",
name: "A name",
description: "A description",
max: 27,
min: 12.5,
}

{type: "numeric::step",
name: "A name",
description: "A description",
max: 27,
min: 12.5,
start: 12.5
step: 2
}

{type: "numeric::number",
name: "A name",
description: "A description",
value: 36
}

{type: "numeric::set",
name: "A name",
description: "A description",
value: [36, 29.0]
}


internally all values are Decimals are are cast to floats or ints only for rendering

VALUE_TYPE_NUMERIC_NUMBER = "numeric::number"
VALUE_TYPE_NUMERIC_SET = "numeric::set"
VALUE_TYPE_NUMERIC_RANGE = "numeric::range"
VALUE_TYPE_NUMERIC_STEP = "numeric::step"


"""
from copy import deepcopy
from decimal import Decimal
from base_values import BaseWinnowValue
from winnow.exceptions import OptionsExceptionFailedValidation, OptionsExceptionIncompatibleTypes, OptionsExceptionNotAllowed

from winnow.constants import *

class NumericWinnowValue(BaseWinnowValue):


    @classmethod
    def from_value(cls, value):
        if isinstance(value, list):
            try:
                decimal_list = [Decimal(v) for v in value]
            except:
                raise OptionsExceptionFailedValidation("NumericSieveValue unrecognised value type")
            numeric = NumericSetWinnowValue(decimal_list)
            if numeric is None:
                raise OptionsExceptionFailedValidation("NumericSieveValue: empty set")
            return numeric

        elif isinstance(value, dict):

            numeric_type = value[u"type"]
            if numeric_type == VALUE_TYPE_NUMERIC_NUMBER:
                return NumericNumberWinnowValue(value)
            elif numeric_type == VALUE_TYPE_NUMERIC_SET:
                numeric = NumericSetWinnowValue(value)
                if numeric is None:
                    raise OptionsExceptionFailedValidation("NumericSieveValue: empty set")
                return numeric
            elif numeric_type == VALUE_TYPE_NUMERIC_RANGE:
                return NumericRangeWinnowValue(value)
            elif numeric_type == VALUE_TYPE_NUMERIC_STEP:
                step = NumericStepWinnowValue(value)
                possible = step.possible_values()
                if len(possible) == 0:
                    raise OptionsExceptionFailedValidation("NumericSieveValue: empty set")
                elif len(possible) == 1:
                    return NumericNumberWinnowValue(list(possible)[0])
                else:
                    return step
        else:
            try:
                d = Decimal(value)
            except:
                raise OptionsExceptionFailedValidation("NumericSieveValue unrecognised value type")
            return NumericNumberWinnowValue(d)


    def check_class(self, other):
        if not issubclass(other.__class__, NumericWinnowValue):
            raise OptionsExceptionIncompatibleTypes("sieve value types must match")


    def issubset(self, other):
        self.check_class(other)
        #do all possible things that satisfy me satisfy the other?

        if self.has_value_set:
            this_possible_values = self.possible_values()
        if other.has_value_set:
            that_possible_values = other.possible_values()

        if not self.has_value_set and not other.has_value_set:
            if self.min  < other.min:
                return False
            if self.max  > other.max:
                return False

        if self.has_value_set and other.has_value_set:
            if not this_possible_values.issubset(that_possible_values):
                return False

        if self.has_value_set and not other.has_value_set:
            if max(this_possible_values) > other.max:
                return False
            if min(this_possible_values) < other.min:
                return False

        if not self.has_value_set and other.has_value_set:
            if self.min < min(that_possible_values):
                return False
            if self.max > max(that_possible_values):
                return False

        return True





    def isdisjoint(self, other):
        return self.intersection(other) is None


class NumericNumberWinnowValue(NumericWinnowValue):

    type = VALUE_TYPE_NUMERIC_NUMBER
    is_determined = True
    has_value_set = True

    def __init__(self, value):

        super(NumericNumberWinnowValue, self).__init__(value)

        if isinstance(value, Decimal):
            self.number = value
        else:
            number = value[u"value"]
            if not isinstance(number, Decimal):
                raise OptionsExceptionFailedValidation("NumericNumberSieveValue must be a Decimal")
            self.number = number


    def possible_values(self):
        return {self.number}

    def get_default(self):
        return self.number


    def as_json(self):

        as_json =  {
            "type": self.type,
            "value": self.number
        }

        return self.update_with_info(as_json)

    def intersection(self, other):

        self.check_class(other)
        intersects = False

        if type(other) in (NumericNumberWinnowValue, NumericSetWinnowValue, NumericStepWinnowValue):
            if self.number in other.possible_values():
                intersects = True
        elif type(other) == NumericRangeWinnowValue:
            if self.number >= other.min and self.number <= other.max:
                intersects = True
        else:
            raise OptionsExceptionFailedValidation("intersection of NumericNumberSieveValue failed")

        if intersects:
            info = self.get_merged_info(other)
            info[u"value"] = self.number
            return NumericNumberWinnowValue(info)
        else:
            return None


class NumericSetWinnowValue(NumericWinnowValue):

    type = VALUE_TYPE_NUMERIC_SET
    is_determined = False
    has_value_set = True


    def __new__(cls, value):

        if isinstance(value, list) or isinstance(value, set):
            as_list = value
            if len(as_list) > MAX_VALUE_SET_SIZE:
                raise OptionsExceptionNotAllowed("maximum value set size exceeded")
            elif len(as_list) == 0:
                print "should be this"
                return None
            elif len(as_list) == 1:
                return NumericNumberWinnowValue(list(as_list)[0])
            else:
                return NumericWinnowValue.__new__(cls)
        else:
            as_list = value[u"value"]
            if not (isinstance(as_list, list) or isinstance(as_list, set)):
                raise OptionsExceptionFailedValidation("NumericNumberSieveValue must be a Decimal")
            if len(as_list) > MAX_VALUE_SET_SIZE:
                raise OptionsExceptionNotAllowed("maximum value set size exceeded")
            elif len(as_list) == 0:
                return None
            elif len(as_list) == 1:
                v = deepcopy(value)
                v[u"value"] = list(as_list)[0]
                return NumericNumberWinnowValue(v)
            else:
                return NumericWinnowValue.__new__(cls)


    def __init__(self, value):

        super(NumericSetWinnowValue, self).__init__(value)

        if isinstance(value, list) or isinstance(value, set):
            self.as_list = value
        else:
            as_list = value[u"value"]
            if not (isinstance(as_list, list) or isinstance(as_list, set)):
                raise OptionsExceptionFailedValidation("NumericNumberSieveValue must be a Decimal")
            self.as_list = as_list


        for v in self.as_list:
            if not isinstance(v, Decimal):
                print v
                raise OptionsExceptionFailedValidation("NumericSetSieveValue all values must be Decimals")

        if len(self.as_list) == 0:
            raise OptionsExceptionFailedValidation("NumericSetSieveValue: empty set")

        if len(self.as_list) == 1:
            raise OptionsExceptionFailedValidation("NumericSetSieveValue: set with one value should have been cast into NumericNumberSieveValue")


    def possible_values(self):
        return set(self.as_list)

    def get_default(self):
        return min(self.as_list)


    def intersection(self, other):

        self.check_class(other)
        if type(other) == NumericRangeWinnowValue:
            values = [v for v in self.possible_values() if v >= other.min and v <= other.max]
        else:
            values = self.possible_values().intersection(other.possible_values())
        info = self.get_merged_info(other)
        info[u"value"] = values
        return NumericSetWinnowValue(info)


    def as_json(self):
        as_json = {
            "type": self.type,
            "value": list(self.as_list)
        }

        return self.update_with_info(as_json)


"""
a range defined by inclusive maximum and minimum
"""

class NumericRangeWinnowValue(NumericWinnowValue):

    type = VALUE_TYPE_NUMERIC_RANGE
    is_determined = False
    has_value_set = False

    def __init__(self, value):

        super(NumericRangeWinnowValue, self).__init__(value)

        self.max = value[u"max"]
        self.min = value[u"min"]
        if self.max < self.min:
            raise OptionsExceptionFailedValidation("NumericRangeSieveValue: max %s less than min %s" % (self.max, self.min))

    def get_default(self):
        return self.min

    def possible_values(self):
        return None

    def intersection(self, other):

        self.check_class(other)
        if type(other) == NumericRangeWinnowValue:

            new_max = min(self.max, other.max)
            new_min = max(self.min, other.min)
            if new_max < new_min:
                return None
            info = self.get_merged_info(other)
            info[u"max"] = new_max
            info[u"min"] = new_min
            return NumericRangeWinnowValue(info)

        if type(other) == NumericStepWinnowValue:
            new_max = min(self.max, other.max)
            new_min = max(self.min, other.min)
            if new_max < new_min:
                return None
            try:
                info = self.get_merged_info(other)
                info[u"max"] = new_max
                info[u"min"] = new_min
                info[u"step"] = other.step
                info[u"start"] = other.start
                sieve = NumericStepWinnowValue.make(info)
            except OptionsExceptionFailedValidation:
                return None
            return sieve
        else:
            values = [v for v in other.possible_values() if v >= self.min and v <= self.max]
            return NumericSetWinnowValue(values)


    def as_json(self):
        as_json =  {
            "type": self.type,
            "max": self.max,
            "min":self.min,
        }

        return self.update_with_info(as_json)


class NumericStepWinnowValue(NumericRangeWinnowValue):

    type = VALUE_TYPE_NUMERIC_STEP
    is_determined = False
    has_value_set = True


    @classmethod
    def make(cls, value):

        step = cls(value)
        poss = step.possible_values()
        if len(poss) == 1:
            kwargs = {
                u"value": poss[0]
            }
            if value.get(u"name") != None:
                kwargs[u"name"] = value.get(u"name")
            if value.get(u"description") != None:
                kwargs[u"description"] = value.get(u"description")
            if value.get(u"image_url") != None:
                kwargs[u"image_url"] = value.get(u"image_url")
            if value.get(u"scopes") != None:
                kwargs[u"scopes"] = value.get(u"scopes")

            return NumericNumberWinnowValue(kwargs)
        return step

    def __init__(self, value):

        super(NumericStepWinnowValue, self).__init__(value)
        self.start = value[u"start"]
        self.step = value[u"step"]

        if len(self.possible_values()) == 0:

            raise OptionsExceptionFailedValidation("NumericStepSieveValue: empty set")


    def intersection(self, other):

        self.check_class(other)

        if type(other) == NumericRangeWinnowValue:
            new_max = min(self.max, other.max)
            new_min = max(self.min, other.min)

            if new_max < new_min:
                return None
            try:
                info = self.get_merged_info(other)
                info[u"max"] = new_max
                info[u"min"] = new_min
                info[u"step"] = self.step
                info[u"start"] = self.start
                sieve = NumericStepWinnowValue.make(info)
            except OptionsExceptionFailedValidation:
                return None
            return sieve
        else:
            values = self.possible_values().intersection(other.possible_values())
            info = self.get_merged_info(other)
            info[u"value"] = values
            return NumericSetWinnowValue(info)

    def get_default(self):
        return min(self.possible_values())

    def possible_values(self):
        poss = []
        v = self.start
        while v <= self.max:
            if v >= self.min and v <= self.max:
                poss.append(v)
            v += self.step
        return set(poss)


    def as_json(self):
        as_json = {
            "type": self.type,
            "max": self.max,
            "min":self.min,
            "start": self.start,
            "step": self.step
        }

        return self.update_with_info(as_json)
