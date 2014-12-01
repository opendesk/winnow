from jsonschema import validate, ValidationError
import json
import time
import hashlib
import requests
from product_exceptions import ProductExceptionFailedValidation, ProductExceptionEmptyOptionValues, ProductExceptionLookupFailed

from copy import deepcopy




class Sieve(object):

    SIEVE_TYPE = u"base"

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
            "options": {
                "type": "object",
                "patternProperties": {
                    "[a-z]": {"type": "object",
                        "patternProperties": {
                        "[a-z]": {"oneOf": [{"type": "array"}, {"type": "string"}, {"type": "object"}, {"type": "number"}]},
                        },
                        "additionalProperties": False
                    },
                },
                "additionalProperties": False
            },
        },
        "required": ["name", "description", "options"],
    }




    def __init__(self, json_dict):


        self.json_dict = deepcopy(json_dict)

        try:
            if self.json_dict.get(u"type") is None:
                self.json_dict[u"type"] = self.SIEVE_TYPE
        except AttributeError, e:
            raise ProductExceptionFailedValidation(e)



        try:
            validate(self.json_dict, Sieve.SIEVE_SCHEMA)
        except ValidationError, e:
            raise ProductExceptionFailedValidation(e)
        except AttributeError, e:
            raise ProductExceptionFailedValidation(e)

        for option_set_name, option_set in self.json_dict[u"options"].iteritems():
            for key, options in option_set.iteritems():
                if isinstance(options, list) and len(options) == 0:
                    raise ProductExceptionEmptyOptionValues("The key %s has no possible values" % key)




    def get_timestamp(self):
        return unicode(time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()))


    def __getattr__(self, name):
        attr = self.json_dict.get(name)
        if attr is None:
            raise AttributeError(name)
        return attr


    @classmethod
    def from_json(cls, as_json):
        return cls(json.loads(as_json))


    @classmethod
    def from_name_and_options(cls, name, description, options=None):
        d = {"name": name,
             "description": description}

        if options is not None:
            d["options"] = options
        return cls(d)


    def allows(self, other):
        """
        An intersection of keys
        A subset check on values
        """
        for option_set_name in self.options:
            this_keys = self.get_keys(option_set_name)
            that_keys = other.get_keys(option_set_name)
            if this_keys is not None and that_keys is not None:
                all_keys = this_keys.intersection(that_keys)
                if all_keys is not None:
                    for key in this_keys.intersection(that_keys):
                        this = self.options_as_set(option_set_name, key)
                        that = other.options_as_set(option_set_name, key)
                        if not that.issubset(this):
                            return False

        return True


    def _merge_values(self, other, option_set_name, key):
        self_values = self.options[option_set_name].get(key)
        other_values = other.options[option_set_name].get(key)
        if self_values is None:
            return other_values
        elif other_values is None:
            return self_values
        else:
            this = self.options_as_set(option_set_name, key)
            that = other.options_as_set(option_set_name, key)
            values = list(this.intersection(that))
            if values == []:
                raise ProductExceptionEmptyOptionValues("The key %s has no possible values when %s is merged with %s" % (key, self.uri, other.uri))
            values.sort()
            return values


    def _patch_values(self, other, option_set_name, key):
        self_values = self.options[option_set_name].get(key)
        other_values = other.options[option_set_name].get(key)
        if self_values is None:
            return other_values
        else:
            return self_values


    def patch(self, other):
        """
        A union of all keys
        Self values overwrite others
        """

        return self.combine(other, self._patch_values)


    def merge(self, other):
        """
        A union of all keys
        An intersection of values
        """

        return self.combine(other, self._merge_values)


    def combine(self, other, combine_func):

        json_dict = deepcopy(self.json_dict)
        options = {}
        this_option_set_names = self.get_option_set_names()
        that_option_set_names = other.get_option_set_names()

        for option_set_name in this_option_set_names.union(that_option_set_names):
            this_keys = self.get_keys(option_set_name)
            that_keys = other.get_keys(option_set_name)
            if this_keys is None:
                options[option_set_name] = deepcopy(other.options[option_set_name])
            elif that_keys is None:
                options[option_set_name] = deepcopy(self.options[option_set_name])
            else:
                option_set = {}
                options[option_set_name] = option_set
                for key in this_keys.union(that_keys):
                    option_set[key] = combine_func(other, option_set_name, key)

        json_dict["options"] = options
        return self.__class__(json_dict)



    def extract(self, option_set_names):
        """
        extracts a subset from the document as a new doc
        """
        json_dict = deepcopy(self.json_dict)
        options = {}
        for option_set_name in self.get_option_set_names():
            if option_set_name in option_set_names:
                options[option_set_name] = deepcopy(self.options[option_set_name])

        json_dict["options"] = options
        return self.__class__(json_dict)


    def match(self, others):
        return [other for other in others if self.allows(other)]

    def reverse_match(self, others):
        return [other for other in others if other.allows(self)]


    def get_option_set_names(self):
        return set(self.json_dict["options"].keys())


    def get_keys(self, option_set_name):
        option_set = self.json_dict["options"].get(option_set_name)
        if option_set is None:
            return None
        return set(option_set.keys())


    def options_as_set(self, option_set, key):
        value = self.json_dict["options"][option_set].get(key)
        if isinstance(value, list):
            return set(value)
        elif isinstance(value, unicode):
            return set([value])
        else:
            raise Exception("unknown type for option values %s" % value)


    def get_uri(self):
        return u"%s/%s" % (self.SIEVE_TYPE, self.name)



class PublishedSieve(Sieve):

    SIEVE_TYPE = u"base"

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
            "history": {
                "type": "array"
            },
            "created": {
                "type": "string"
            },
            "upstream": {
                "type": "string"
            },
            "options": {
                "type": "object",
                "patternProperties": {
                    "[a-z]": {"type": "object",
                        "patternProperties": {
                        "[a-z]": {"oneOf": [{"type": "array"}, {"type": "string"}, {"type": "object"}, {"type": "number"}]},
                        },
                        "additionalProperties": False
                    },
                },
                "additionalProperties": False
            },
        },
        "required": ["name", "description", "options", "uri", "history", "created"],
    }


    def __init__(self, json_dict):

        super(PublishedSieve, self).__init__(json_dict)

        try:
            if self.json_dict.get(u"uri") is None:
                self.json_dict[u"uri"] = self.get_uri()

            if self.json_dict.get(u"created") is None:
                self.json_dict[u"created"] = unicode(time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()))

            if self.json_dict.get(u"history") is None:
                self.json_dict[u"history"] = ["start::%s" % self.get_version_uri()]
                self._update_frozen_uri()

        except AttributeError, e:
            raise ProductExceptionFailedValidation(e)


        try:
            validate(self.json_dict, PublishedSieve.SIEVE_SCHEMA)
            validate(self.json_dict, self.SIEVE_SCHEMA)
        except ValidationError, e:
            raise ProductExceptionFailedValidation(e)


    def duplicate(self):
        return self.__class__(self.json_dict)


    def merge(self, other):
        merged = super(PublishedSieve, self).merge(other)
        merged.history.append("merge::%s" % other.get_version_uri())
        merged._update_frozen_uri()
        return merged


    def patch(self, other):
        patched = super(PublishedSieve, self).patch(other)
        patched.history.append("patch::%s" % other.get_version_uri())
        patched._update_frozen_uri()
        return patched


    def extract(self, extractions):
        extracted = super(PublishedSieve, self).extract(extractions)
        extracted.history.append("extract::%s" % "::".join(extractions))
        extracted._update_frozen_uri()
        return extracted


    def patch_upstream(self, db):
        patched = self._patch_upstream(db, self.json_dict.get("upstream"))
        if patched.json_dict.get("upstream") is not None:
            del patched.json_dict["upstream"]
        return patched


    def _update_frozen_uri(self):
        self.json_dict[u"frozen_uri"] = self._get_frozen_uri()


    def _patch_upstream(self, db, upstream_uri):
        if upstream_uri is None:
            return self.duplicate()

        upstream_json = db.get(upstream_uri)
        if upstream_json is None:
            try:
                rsp = requests.get(upstream_uri)
                if rsp.status_code < 300:
                    upstream_json = rsp.json()
                else:
                    raise ProductExceptionLookupFailed("Couldn't find the upstream model")
            except Exception, e:
                raise ProductExceptionLookupFailed(e)

        upstream_sieve = self.__class__.from_json(upstream_json)
        new_upstream_uri = upstream_sieve.json_dict.get(u"upstream")
        patched = self.patch(upstream_sieve)
        if new_upstream_uri is not None:
            patched = patched._patch_upstream(db, new_upstream_uri)
        return patched


    def _get_frozen_uri(self):
        md5 = hashlib.md5()
        md5.update(str(self.history))
        frozen_id = md5.hexdigest()
        return "%s/frozen/%s" % (self.get_uri(), frozen_id)

    def get_version_uri(self):
        return u"%s@xxxxxxxx" % self.uri


    def _get_is_frozen(self):
        return self.json_dict.get("frozen_uri") is not None


    def save(self, db, overwrite=True):
        db.set(self.uri, json.dumps(self.json_dict), overwrite=overwrite)


    is_frozen = property(_get_is_frozen)






























