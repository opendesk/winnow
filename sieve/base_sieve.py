from jsonschema import validate, ValidationError
import json
import time
import hashlib
import requests

import uuid
import decimal
from sieve.product_exceptions import ProductExceptionFailedValidation, ProductExceptionEmptyOptionValues, ProductExceptionLookupFailed
from sieve.options_set import OptionsSet
from sieve.utils import get_doc_hash, json_loads, json_dumps

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
                    "[a-z]": {"oneOf": [{"type": "array"}, {"type": "string"}, {"type": "object"}, {"type": "number"}]},
                },
                "additionalProperties": False
            },
        },
        "required": ["name", "description", "options"],
    }


    def __init__(self, doc):


        self.doc = deepcopy(doc)

        try:
            validate(self.doc, Sieve.SIEVE_SCHEMA)
        except ValidationError, e:
            raise ProductExceptionFailedValidation(e)
        except AttributeError, e:
            raise ProductExceptionFailedValidation(e)

        for key, options in self.doc[u"options"].iteritems():
            if isinstance(options, list) and len(options) == 0:
                raise ProductExceptionEmptyOptionValues("The key %s has no possible values" % key)

        self.options = OptionsSet(self.doc[u"options"])

    def get_timestamp(self):
        return unicode(time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()))


    def __getattr__(self, name):
        attr = self.doc.get(name)
        if attr is None:
            raise AttributeError(name)
        return attr


    @classmethod
    def from_json(cls, as_json):
        return cls(json_loads(as_json))


    @classmethod
    def from_name_and_options(cls, name, description, options=None):
        d = {"name": name,
             "description": description}

        if options is not None:
            d["options"] = options
        return cls(d)


    def intersects(self, other):
        return self.options.intersects(other.options)

    def allows(self, other):
        return self.options.allows(other.options)


    def patch(self, other):
        doc = deepcopy(self.doc)
        doc["options"] = self.options.patch(other.options).store
        return self.__class__(doc)


    def merge(self, other):
        doc = deepcopy(self.doc)
        doc["options"] = self.options.merge(other.options).store
        return self.__class__(doc)


    def extract(self, key_names):
        doc = deepcopy(self.doc)
        doc["options"] = self.options.extract(key_names).store
        return self.__class__(doc)


    def match(self, others):
        return [other for other in others if self.options.allows(other.options)]


    def match_intersects(self, others):
        return [other for other in others if self.options.intersects(other.options)]


    def reverse_match(self, others):
        return [other for other in others if other.options.allows(self.options)]


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
            "upstream": {
                "type": "string"
            },
            "options": {
                "type": "object",
                "patternProperties": {
                    "[a-z]": {"oneOf": [{"type": "array"}, {"type": "string"}, {"type": "object"}, {"type": "number"}]},
                },
                "additionalProperties": False
            },
        },
        "required": ["name", "description", "options"],
    }

    def __init__(self, doc, doc_hash=None, key=None, created=None, history=None, snapshot=False):

        super(PublishedSieve, self).__init__(doc)

        try:
            if doc_hash:
                self.doc_hash = doc_hash
            else:
                self.doc_hash = get_doc_hash(json_dumps(doc))
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
        print "canonical"
        return self.__class__.from_json(db.get(self.get_canonical_uri()))


    def duplicate(self):
        print "duplicate"
        return self.__class__(self.doc, created=self.created, history=self.history)


    def add_history_entry(self, action_name, uri):
        self.history.append([action_name, uri])


    def merge(self, other):
        merged = super(PublishedSieve, self).merge(other)
        self._inherit(merged)
        merged.add_history_entry(u"merge", other.uri)
        return merged


    def patch(self, other):
        patched = super(PublishedSieve, self).patch(other)
        self._inherit(patched)
        patched.add_history_entry(u"patch", other.uri)
        return patched


    def extract(self, extractions):
        extracted = super(PublishedSieve, self).extract(extractions)
        self._inherit(extracted)
        extracted.add_history_entry(u"extract",  extractions)
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
        db.set(self.key, json_dumps(self.get_json()), uri=self.uri,  index=index)

    @classmethod
    def from_doc(cls, doc_json):
        doc_hash = get_doc_hash(doc_json)
        return cls(json_loads(doc_json), doc_hash=doc_hash)


    @classmethod
    def from_json(cls, as_json):

        as_dict = json_loads(as_json)
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

















