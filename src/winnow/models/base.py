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


    @classmethod
    def patched(cls, db, doc, kwargs, source_a, source_b):
        wv = cls(db, kwargs)
        winnow.patch(source_a, source_b, wv, doc)
        db.set(wv.kwargs[u"uuid"], wv.kwargs)
        return wv


    def scoped(self, db, doc, scopes, kwargs={}):
        wv = self.__class__(self.db, kwargs)
        winnow.scope(self, scopes, wv, doc)
        db.set(wv.kwargs[u"uuid"], wv.kwargs)
        return wv

    def expanded(self, kwargs={}):
        wv = self.__class__(self.db, kwargs)
        winnow.expand(self, wv)
        self.db.set(wv.kwargs[u"uuid"], wv.kwargs)
        return wv


    def allows(self, other):
        return winnow.allows(self, other)

    def intersects(self, other):
        return winnow.intersects(self, other)

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

    def add_history_action(self, kwargs):
        history = self.kwargs.get(u"history")
        if history is None:
            history = self.kwargs[u"history"] = []

        history.append(kwargs)

    def get_options_dict(self):
        return self.kwargs[u"doc"][u"options"]

    def set_doc(self, doc):
        self.kwargs[u"doc"] = doc

    def get_doc(self):
        return self.kwargs[u"doc"]

    def get_ref(self, ref):
        version = self.db.get(ref)
        if version is None:
            return None
        return version[u"doc"]


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
            return WinnowVersion(self.db, kwargs)

    def history_is_empty(self):
        return  not bool(self.kwargs.get(u"history"))