from jsonschema import validate, ValidationError
import json
import time
import hashlib
import requests
import uuid
from product_exceptions import ProductExceptionFailedValidation, ProductExceptionEmptyOptionValues, ProductExceptionLookupFailed

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from copy import deepcopy


def get_doc_hash(data):
    s = hashlib.sha1()
    s.update("blob %u\0" % len(data))
    s.update(data)
    return unicode(s.hexdigest())

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




    def __init__(self, doc):


        self.doc = deepcopy(doc)

        # try:
        #     if self.doc.get(u"type") is None:
        #         self.doc[u"type"] = self.SIEVE_TYPE
        # except AttributeError, e:
        #     raise ProductExceptionFailedValidation(e)

        try:
            validate(self.doc, Sieve.SIEVE_SCHEMA)
        except ValidationError, e:
            raise ProductExceptionFailedValidation(e)
        except AttributeError, e:
            raise ProductExceptionFailedValidation(e)

        for option_set_name, option_set in self.doc[u"options"].iteritems():
            for key, options in option_set.iteritems():
                if isinstance(options, list) and len(options) == 0:
                    raise ProductExceptionEmptyOptionValues("The key %s has no possible values" % key)

    def get_timestamp(self):
        return unicode(time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()))


    def __getattr__(self, name):
        attr = self.doc.get(name)
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


    def intersects(self, other):
        """
        An intersection of keys
        An intersection check on values
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
                        if that.isdisjoint(this):
                            return False

        return True


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

        doc = deepcopy(self.doc)
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

        doc["options"] = options
        return self.__class__(doc)



    def extract(self, option_set_names):
        """
        extracts a subset from the document as a new doc
        """
        doc = deepcopy(self.doc)
        options = {}
        for option_set_name in self.get_option_set_names():
            if option_set_name in option_set_names:
                options[option_set_name] = deepcopy(self.options[option_set_name])

        doc["options"] = options
        return self.__class__(doc)


    def match(self, others):
        return [other for other in others if self.allows(other)]

    def match_intersects(self, others):
        return [other for other in others if self.intersects(other)]

    def reverse_match(self, others):
        return [other for other in others if other.allows(self)]


    def get_option_set_names(self):
        return set(self.doc["options"].keys())


    def get_keys(self, option_set_name):
        option_set = self.doc["options"].get(option_set_name)
        if option_set is None:
            return None
        return set(option_set.keys())

    def options_as_set(self, option_set, key):
        value = self.doc["options"][option_set].get(key)
        if isinstance(value, list):
            return set(value)
        elif isinstance(value, unicode):
            return set([value])
        else:
            raise Exception("unknown type for option values %s" % value)

    def get_json(self):
        return self.doc



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
            "key": {
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

    "uri", "history", "history_hash", "created", "snapshot"



    def __init__(self, doc, doc_hash=None, key=None, created=None, history=None, snapshot=False):

        super(PublishedSieve, self).__init__(doc)

        try:
            if doc_hash:
                self.doc_hash = doc_hash
            else:
                self.doc_hash = get_doc_hash(json.dumps(doc, indent=4, sort_keys=True))
            if key:
                self.key = key
            if snapshot:
                self.snapshot = snapshot

            self.uri = u"%s@%s" % (self.get_canonical_uri(), self.doc_hash)

            self.created = created if created else unicode(time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()))
            self.history = history if history else [[u"start", self.uri]]

        except AttributeError, e:
            raise ProductExceptionFailedValidation(e)

        try:
            validate(self.doc, PublishedSieve.SIEVE_SCHEMA)
            validate(self.doc, self.SIEVE_SCHEMA)
        except ValidationError, e:
            raise ProductExceptionFailedValidation(e)

    def canonical(self, db):
        return self.__class__.from_json(db.get(self.get_canonical_uri()))


    def duplicate(self):

        return self.__class__(self.doc, created=self.created, history=self.history)


    def merge(self, other):
        merged = super(PublishedSieve, self).merge(other)
        self._inherit(merged)
        merged.history.append([u"merge", other.uri])
        return merged


    def patch(self, other):
        patched = super(PublishedSieve, self).patch(other)
        self._inherit(patched)
        patched.history.append([u"patch", other.uri])
        return patched


    def extract(self, extractions):
        extracted = super(PublishedSieve, self).extract(extractions)
        self._inherit(extracted)
        extracted.history.append([u"extract",  extractions])
        return extracted


    def take_snapshot(self, db):
        patched = self._patch_upstream(db, self.doc.get("upstream"))
        patched.snapshot = True
        return patched


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
        new_upstream_uri = upstream_sieve.doc.get(u"upstream")
        patched = self.patch(upstream_sieve)
        if new_upstream_uri is not None:
            patched = patched._patch_upstream(db, new_upstream_uri)
        return patched

    def is_snapshot(self):
        return hasattr(self, "snapshot")

    def _inherit(self, new):
        new.history = self.history
        if hasattr(self, "snapshot"):
            new.snapshot = self.snapshot

    def get_canonical_uri(self):
        return u"%s/%s" % (self.SIEVE_TYPE, self.name)


    def save(self, db, index=None):
        if not hasattr(self, "key"):
            self.key = unicode(uuid.uuid4())
        db.set(self.key, json.dumps(self.get_json()), uri=self.uri,  index=index)

    @classmethod
    def from_doc(cls, doc_json):
        doc_hash = get_doc_hash(doc_json)
        return cls(json.loads(doc_json), doc_hash=doc_hash)


    @classmethod
    def from_json(cls, as_json):

        as_dict = json.loads(as_json)
        kwargs = {}

        for k in ["doc_hash", "key", "history", "created", 'snapshot']:
            v = as_dict.get(k)
            if v is not None:
                kwargs[k] = v
                del as_dict[k]

        return cls(as_dict["doc"], **kwargs)


    def get_json(self):

        as_json = {}

        as_json[u"doc"] = deepcopy(self.doc)
        as_json[u"uri"] = self.uri
        as_json[u"history"] = self.history
        as_json[u"created"] = self.created
        as_json[u"type"] = self.SIEVE_TYPE
        if hasattr(self, "snapshot"):
            as_json[u"snapshot"] = True

        return as_json

















