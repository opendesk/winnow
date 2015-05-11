from base_values import BaseWinnowValue
from winnow.exceptions import OptionsExceptionFailedValidation
from winnow.constants import *

class BooleanWinnowValue(BaseWinnowValue):

    type = VALUE_TYPE_BOOLEAN

    def __init__(self, value):

        super(BooleanWinnowValue, self).__init__(value)

        if isinstance(value, bool):
            self.true = value
            self.undetermined = False
        elif isinstance(value, list):
            self.set_list(value)
        elif isinstance(value, dict):
            v = value[u"value"]
            if isinstance(v, bool):
                self.true = v
                self.undetermined = False
            elif isinstance(v, list):
                self.set_list(v)
        else:
            raise OptionsExceptionFailedValidation("BooleanWinnowValue bad type")

    def set_list(self, l):
        if len(l) != 2:
            raise OptionsExceptionFailedValidation("Bool list can only have two members")
        if not isinstance(l[0], bool):
            raise OptionsExceptionFailedValidation("Bool list must have only true and false")
        if not isinstance(l[1], bool):
            raise OptionsExceptionFailedValidation("Bool list must have only true and false")
        if l[0] == l[1]:
            raise OptionsExceptionFailedValidation("Bool list must have only true and false")
        self.true = None
        self.undetermined = True


    @classmethod
    def from_value(cls, value):
        return cls(value)

    def get_default(self):
        return False

    def as_json(self):

        as_json =  {
            "type": self.type,
            "value": [True, False] if self.undetermined else self.true
        }

        return self.update_with_info(as_json)


    def isdisjoint(self, other):
        if self.undetermined or other.undetermined:
            return False
        return self.true != other.true


    def issubset(self, other):
        if other.undetermined:
            return True
        return self.true == other.true


    def intersection(self, other):
        self.check_class(other)
        intersects = False
        if self.undetermined and other.undetermined:
            intersects = True
            v = [True, False]
        elif self.undetermined:
            intersects = True
            v = other.true
        elif other.undetermined:
            intersects = True
            v = self.true
        elif self.true == other.true:
            intersects = True
            v = self.true
        else:
            intersects = False
            v = None
        if intersects:
            info = self.get_merged_info(other)
            info[u"value"] = v
            return BooleanWinnowValue(info)
        else:
            return None


