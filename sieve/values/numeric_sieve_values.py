
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

from decimal import Decimal
from base_sieve_values import BaseSieveValue
from sieve.product_exceptions import ProductExceptionFailedValidation, ProductExceptionIncompatibleTypes, ProductExceptionNoAllowed

from consts import *

class NumericSieveValue(BaseSieveValue):

    @classmethod
    def from_value(cls, value):

        if isinstance(value, list):
            try:
                decimal_list = [Decimal(v) for v in value]
            except:
                raise ProductExceptionFailedValidation("NumericSieveValue unrecognised value type")
            # numeric = NumericSetSieveValue.make(decimal_list)
            numeric = NumericSetSieveValue(decimal_list)
            if numeric is None:
                raise ProductExceptionFailedValidation("NumericSieveValue: empty set")
            return numeric


        elif isinstance(value, dict):


            numeric_type = value[u"type"]
            if numeric_type == VALUE_TYPE_NUMERIC_NUMBER:
                return NumericNumberSieveValue(value[u"value"])
            elif numeric_type == VALUE_TYPE_NUMERIC_SET:
                # numeric = NumericSetSieveValue.make(value[u"value"])
                numeric = NumericSetSieveValue(value[u"value"])
                if numeric is None:
                    raise ProductExceptionFailedValidation("NumericSieveValue: empty set")
                return numeric
            elif numeric_type == VALUE_TYPE_NUMERIC_RANGE:
                return NumericRangeSieveValue(value[u"max"], value[u"min"])
            elif numeric_type == VALUE_TYPE_NUMERIC_STEP:
                step = NumericStepSieveValue(value[u"max"], value[u"min"], value[u"start"], value[u"step"])
                possible = step.possible_values()
                if len(possible) == 0:
                    raise ProductExceptionFailedValidation("NumericSieveValue: empty set")
                elif len(possible) == 1:
                    return NumericNumberSieveValue(list(possible)[0])
                else:
                    return step
        else:
            try:
                d = Decimal(value)
            except:
                raise ProductExceptionFailedValidation("NumericSieveValue unrecognised value type")

            return NumericNumberSieveValue(d)


    def check_class(self, other):
        if not issubclass(other.__class__, NumericSieveValue):
            raise ProductExceptionIncompatibleTypes("sieve value types must match")


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


class NumericNumberSieveValue(NumericSieveValue):

    type = VALUE_TYPE_NUMERIC_NUMBER
    is_determined = True
    has_value_set = True

    def __init__(self, number):

        if not isinstance(number, Decimal):
            raise ProductExceptionFailedValidation("NumericNumberSieveValue must be a Decimal")

        self.number = number

    def possible_values(self):
        return {self.number}


    def as_json(self):
        return {
            "type": self.type,
            "value": self.number
        }

    def intersection(self, other):

        self.check_class(other)
        intersects = False

        if type(other) in (NumericNumberSieveValue, NumericSetSieveValue, NumericStepSieveValue):
            if self.number in other.possible_values():
                intersects = True
        elif type(other) == NumericRangeSieveValue:
            if self.number >= other.min and self.number <= other.max:
                intersects = True
        else:
            raise ProductExceptionFailedValidation("intersection of NumericNumberSieveValue failed")

        if intersects:
            return NumericNumberSieveValue(self.number)
        else:
            return None


class NumericSetSieveValue(NumericSieveValue):

    type = VALUE_TYPE_NUMERIC_SET
    is_determined = False
    has_value_set = True


    def __new__(cls, as_list):
        if len(as_list) > MAX_VALUE_SET_SIZE:
            raise ProductExceptionNoAllowed("maximum value set size exceeded")
        elif len(as_list) == 0:
            return None
        elif len(as_list) == 1:
            return NumericNumberSieveValue(list(as_list)[0])
        else:
            return NumericSieveValue.__new__(cls)


    def __init__(self, as_list):
        self.as_list = as_list

        for v in as_list:
            if not isinstance(v, Decimal):
                raise ProductExceptionFailedValidation("NumericSetSieveValue all values must be Decimals")

        if len(self.as_list) == 0:
            raise ProductExceptionFailedValidation("NumericSetSieveValue: empty set")

        if len(self.as_list) == 1:
            raise ProductExceptionFailedValidation("NumericSetSieveValue: set with one value should have been cast into NumericNumberSieveValue")


    def possible_values(self):
        return set(self.as_list)


    def intersection(self, other):

        self.check_class(other)
        if type(other) == NumericRangeSieveValue:
            values = [v for v in self.possible_values() if v >= other.min and v <= other.max]
        else:
            values = self.possible_values().intersection(other.possible_values())
        # return NumericSetSieveValue.make(values)
        return NumericSetSieveValue(values)


    def as_json(self):
        return {
            "type": self.type,
            "value": self.as_list
        }


"""
a range defined by inclusive maximum and minimum
"""

class NumericRangeSieveValue(NumericSieveValue):

    type = VALUE_TYPE_NUMERIC_RANGE
    is_determined = False
    has_value_set = False

    def __init__(self, max, min):

        self.max = max
        self.min = min
        if self.max < self.min:
            raise ProductExceptionFailedValidation("NumericRangeSieveValue: max %s less than min %s" % (self.max, self.min))


    def possible_values(self):
        return None

    def intersection(self, other):

        self.check_class(other)
        if type(other) == NumericRangeSieveValue:

            new_max = min(self.max, other.max)
            new_min = max(self.min, other.min)
            if new_max < new_min:
                return None
            return NumericRangeSieveValue(new_max, new_min)

        if type(other) == NumericStepSieveValue:
            new_max = min(self.max, other.max)
            new_min = max(self.min, other.min)
            if new_max < new_min:
                return None
            try:
                sieve = NumericStepSieveValue.make(new_max, new_min, other.start, other.step)
            except ProductExceptionFailedValidation:
                return None
            return sieve
        else:
            values = [v for v in other.possible_values() if v >= self.min and v <= self.max]
            return NumericSetSieveValue(values)


    def as_json(self):
        return {
            "type": self.type,
            "max": self.max,
            "min":self.min,
        }


class NumericStepSieveValue(NumericRangeSieveValue):

    type = VALUE_TYPE_NUMERIC_STEP
    is_determined = False
    has_value_set = True


    @classmethod
    def make(cls, max, min, start, step):
        step = cls( max, min, start, step)
        poss = step.possible_values()
        if len(poss) == 1:
            return NumericNumberSieveValue(poss[0])
        return step

    def __init__(self, max, min, start, step):

        super(NumericStepSieveValue, self).__init__(max, min)

        self.start = start
        self.step = step

        if len(self.possible_values()) == 0:

            raise ProductExceptionFailedValidation("NumericStepSieveValue: empty set")


    def intersection(self, other):

        self.check_class(other)

        if type(other) == NumericRangeSieveValue:
            new_max = min(self.max, other.max)
            new_min = max(self.min, other.min)

            if new_max < new_min:
                return None
            try:
                sieve = NumericStepSieveValue.make(new_max, new_min, self.start, self.step)
            except ProductExceptionFailedValidation:
                return None
            return sieve
        else:
            values = self.possible_values().intersection(other.possible_values())

            return NumericSetSieveValue(values)


    def possible_values(self):
        poss = []
        v = self.start
        while v <= self.max:
            if v >= self.min and v <= self.max:
                poss.append(v)
            v += self.step
        return set(poss)


    def as_json(self):
        return {
            "type": self.type,
            "max": self.max,
            "min":self.min,
            "start": self.start,
            "step": self.step
        }
