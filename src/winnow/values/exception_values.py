from winnow.constants import VALUE_TYPE_EXCEPTION


class ExceptionWinnowValue(object):

    def __init__(self, key, values, context=None):

        self.key = key
        self.values = values
        self.context = context

    @property
    def default(self):
        return None


    def as_json(self):
        return {
            "key": self.key,
            "type": VALUE_TYPE_EXCEPTION,
            "values": self.values,
            "context": self.context
        }

    @classmethod
    def from_value(cls, value):
        return cls(value["key"], value["values"], context=value["context"])