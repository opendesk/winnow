import uuid
import winnow
from winnow.interface import OptionsInterface
from winnow.utils import json_dumps
from copy import deepcopy

from winnow.constants import *

class WinnowVersion(OptionsInterface):

    def __init__(self, db, kwargs):
        self.kwargs = deepcopy(kwargs)
        self.db = db
        if self.kwargs.get("uuid") is None:
            self.kwargs["uuid"] = unicode(uuid.uuid4())

    def __str__(self):
        return json_dumps(self.kwargs)


    @classmethod
    def get_from_path(cls, db, path):
        kwargs = db.get(path)
        return None if kwargs is None else cls(db, kwargs)

    @classmethod
    def get_from_id(cls, db, id):
        kwargs = db.get(id)
        return None if kwargs is None else cls(db, kwargs)

    @classmethod
    def get_from_id(cls, db, id):
        kwargs = db.get(id)
        return None if kwargs is None else cls(db, kwargs)

    ##  oo wrappers around winnow operations

    def validate(self):
        winnow.validate(self.get_doc())

    @classmethod
    def publish(cls, db, as_json):
        winnow.validate(as_json)
        return cls.add_doc(db, as_json)

    @classmethod
    def add_doc(cls, db, doc, kwargs={}):
        wv = cls(db, kwargs)
        winnow.add_doc(wv, doc)
        db.set(wv.kwargs[u"uuid"], wv.kwargs)
        path = wv.kwargs[u"doc"].get(u"path")
        if path is not None:
            db.set(path, wv.kwargs)
        return wv

    @classmethod
    def merged(cls, db, doc, kwargs, source_a, source_b):
        wv = cls(db, kwargs)
        winnow.merge(source_a, source_b, wv, doc)
        db.set(wv.kwargs[u"uuid"], wv.kwargs)
        return wv

    def quantified(self, kwargs={}):
        wv = self.__class__(self.db, kwargs)
        winnow.quantify(self, wv, self.get_doc())
        self.db.set(wv.kwargs[u"uuid"], wv.kwargs)
        return wv

    def scoped(self, scopes, kwargs={}):
        wv = self.__class__(self.db, kwargs)
        winnow.scope(self, scopes, wv, self.get_doc())
        self.db.set(wv.kwargs[u"uuid"], wv.kwargs)
        return wv

    def expanded(self, kwargs={}):
        wv = self.__class__(self.db, kwargs)
        winnow.expand(self, wv)
        self.db.set(wv.kwargs[u"uuid"], wv.kwargs)
        return wv

    def allows(self, other):
        return winnow.allows(self, other)

    def filter_allows(self, possible):
        return winnow.filter_allows(self, possible)

    def filter_allowed_by(self, possible):
        return winnow.filter_allowed_by(self, possible)

    ## OptionsInterface methods

    def set_is_expanded(self):
        self.kwargs[u"is_expanded"] = True

    def set_doc_hash(self, hash):
        self.kwargs[u"doc_hash"] = hash

    def get_doc_hash(self):
        return self.kwargs[u"doc_hash"]

    def get_uuid(self):
        return self.kwargs[u"uuid"]

    def add_history_action(self, action, output_type, input=None, scope=None):
        history = self.kwargs.get(u"history")
        if history is None:
            history = self.kwargs[u"history"] = []

        kwargs = {"action": action,
                  "output_type" : output_type,
                  "input_id": input.get_uuid() if input is not None else None,
                  "scope": scope
        }

        history.append(kwargs)

    def get_options_dict(self):
        try:
            return self.kwargs[u"doc"][u"options"]
        except KeyError:
            return None

    def set_doc(self, doc):
        self.kwargs[u"doc"] = doc


    def get_doc(self):
        return self.kwargs[u"doc"]


    def lookup(self, path):
        kwargs = self.db.get(path)
        if kwargs is None:
            return None
        version = WinnowVersion(self.db, kwargs)
        return version


    def clone_history_from(self, options_interface):
        history = options_interface.kwargs.get(u"history")
        if history is not None:
            self.kwargs[u"history"] = deepcopy(history)

    def get_upstream(self):
        upstream_id = self.kwargs[u"doc"].get(u"upstream")
        if upstream_id is None:
            return None
        else:
            kwargs = self.db.get(upstream_id)
            if kwargs is None:
                return None
            return WinnowVersion(self.db, kwargs)

    def history_is_empty(self):
        return  not bool(self.kwargs.get(u"history"))