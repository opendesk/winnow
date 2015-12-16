from .constants import VALUE_TYPE_EXCEPTION

class OptionsExceptionBase(Exception):pass

class OptionsExceptionFailedValidation(OptionsExceptionBase):pass

class OptionsExceptionIncompatibleTypes(OptionsExceptionBase):pass

class OptionsExceptionNotAllowed(OptionsExceptionBase):pass

# class OptionsExceptionEmptyOptionValues(OptionsExceptionBase):
#
#     def __init__(self, key, values):
#         self.key = key
#         self.values = values
#          msg = "The key %s has no possible values when %s are merged" % (key, [v.as_json() for v in values])
#         super(OptionsExceptionEmptyOptionValues, self).__init__(msg)
#
#     def as_json(self):
#
#         return {
#             "key": self.key,
#             "type": VALUE_TYPE_EXCEPTION,
#             "msg": self.message,
#             "values": [v.as_json() for v in self.values]
#         }
#
#     @classmethod
#     def from_value(cls, value):
#         cls()



class OptionsExceptionSetWithException(OptionsExceptionBase):

    def __init__(self, set, exception_infos):

        self.set = set
        self.exception_infos = exception_infos
        super(OptionsExceptionSetWithException, self).__init__("This set of options contains an empty value")


class OptionsExceptionMissingInterfaceMethod(OptionsExceptionBase):pass

class OptionsExceptionReferenceError(OptionsExceptionBase):pass

class OptionsExceptionKeyError(OptionsExceptionBase):pass