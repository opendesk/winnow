
from winnow.exceptions import OptionsExceptionFailedValidation
from winnow.utils import json_dumps


class BaseWinnowValue(object):

    def check_class(self, other):
        if not self.__class__ == other.__class__:
            raise Exception("sieve value types must match")

    def __str__(self):
        return json_dumps(self.as_json())













