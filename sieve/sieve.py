from jsonschema import validate, ValidationError
import json
import time
from product_exceptions import ProductExceptionFailedValidation




class Sieve(object):

    SIEVE_SCHEMA = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "properties": {
            "name": {
                "type": "string"
            },
            "description": {
                "type": "string"
            },
            "uri": {
                "type": "string"
            },
            "options": {
                "patternProperties": {
                    "[a-z]": {"oneOf": [{"type": "array"}, {"type": "string"}, {"type": "object"}, {"type": "number"}]},
                },
                "additionalProperties": False
            },
            "dependencies": {
                "[a-z]": {"type": "object"},
            }
        },
        "required": ["name", "description", "uri"],
        "definitions": {
            "simpleTypes": {
                "enum": [ "array", "boolean", "integer", "null", "number", "object", "string"]
            },
        },
    }

    def __init__(self, json_dict):

        self.json_dict = json_dict

        try:
            validate(json_dict, self.SIEVE_SCHEMA)
        except ValidationError, e:
            raise ProductExceptionFailedValidation(e)

        if "options" in json_dict.keys():
            self.keys = frozenset(json_dict["options"].keys())
            self.options = {}
            for k, v in json_dict["options"].iteritems():
                if isinstance(v, list):
                    self.options[k] = frozenset(v)
                elif isinstance(v, str):
                    self.options[k] = frozenset([v])
                else:
                    raise Exception("unknown type for option values")


    def __getattr__(self, name):
        attr = self.json_dict.get(name)
        if attr is None:
            raise AttributeError()
        return attr


    @classmethod
    def from_json(cls, as_json):
        return cls(json.loads(as_json))

    @classmethod
    def from_name_and_options(cls, name, uri, description, options=None):
        d = {"name": name,
             "uri": uri,
             "description": description}

        if options is not None:
            d["options"] = options
        return cls(d)


    def allows(self, other):
        """
        An intersection of keys
        A subset check on values
        """

        for key in self.keys.intersection(other.keys):
            if not other.options[key].issubset(self.options[key]):
                return False
        return True


    def merge(self, other, comment=None):
        """
        A union of all keys
        An intersection of values
        """

        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.000000", time.gmtime())

        name = "%s + %s" % (self.name, other.name)
        uri = "something"
        description = """*******************
        Merged on %(datetime)s %(comment)s

        uri: %(self_uri)s
        name: %(self_name)s
        description: %(self_description)s

        uri: %(other_uri)s
        name: %(other_name)s
        description: %(other_description)s
        *******************""" % { "comment": comment,
                "self_uri": self.uri,
                "self_name": self.name,
                "self_description": self.description,
                "other_uri": other.uri,
                "other_name": other.name,
                "other_description": other.description,
                "datetime": timestamp
        }

        options = {}

        for key in self.keys.union(other.keys):
            self_values = self.options.get(key)
            other_values = other.options.get(key)

            if self_values is None:
                options[key] = list(other_values)
            elif other_values is None:
                options[key] = list(self_values)
            else:
                options[key] = list(self_values.intersection(other_values))

        return Sieve.from_name_and_options(name, uri, description, options)





    def patch(self, other, comment=None):
        """
        A union of all keys
        Other values overwrite if present
        """

        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.000000", time.gmtime())

        name = "%s ++ %s" % (self.name, other.name)
        uri = "something"
        description = """*******************
        Patched on %(datetime)s %(comment)s

        uri: %(self_uri)s
        name: %(self_name)s
        description: %(self_description)s

        Patched with:

        uri: %(other_uri)s
        name: %(other_name)s
        description: %(other_description)s
        *******************""" % { "comment": comment,
                "self_uri": self.uri,
                "self_name": self.name,
                "self_description": self.description,
                "other_uri": other.uri,
                "other_name": other.name,
                "other_description": other.description,
                "datetime": timestamp
        }

        options = {}

        for key in self.keys.union(other.keys):
            self_values = self.options.get(key)
            other_values = other.options.get(key)

            if other_values is None:
                options[key] = list(self_values)
            else:
                options[key] = list(other_values)

        return Sieve.from_name_and_options(name, uri, description, options)


    def extract(self, keys, comment=None):
        """
        extracts a subset from the document ans a new doc
        """

        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.000000", time.gmtime())

        name = "%s (%s)" % (self.name, keys)
        uri = "something"
        description = """Extracted keys %(keys)s
        Comment: %(comment)s
        On: %(datetime)s
        From:
        uri: %(self_uri)s
        name: %(self_name)s
        description: %(self_description)s
        """ % { "comment": comment,
                "self_uri": self.uri,
                "self_name": self.name,
                "self_description": self.description,
                "keys": keys,
                "datetime": timestamp
        }

        options = {}

        for key in keys:
            if key in self.keys:
                options[key] = list(self.options[key])

        return Sieve.from_name_and_options(name, uri, description, options)


    def match(self, others):

        return [other for other in others if self.allows(other)]

