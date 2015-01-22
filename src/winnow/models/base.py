import uuid
import winnow
from winnow.interface import OptionsInterface
from copy import deepcopy

from winnow.constants import *






class WinnowVersion(OptionsInterface):

    def __init__(self, db, kwargs):
        self.kwargs = deepcopy(kwargs)
        self.db = db
        if self.kwargs.get("uuid") is None:
            self.kwargs["uuid"] = unicode(uuid.uuid4())

    ##  oo wrappers around winnow operations

    @classmethod
    def add_doc(cls, db, doc, kwargs):
        wv = cls(db, kwargs)
        winnow.add_doc(wv, doc)
        db.set(wv.kwargs[u"uuid"], wv.kwargs)
        return wv

    @classmethod
    def merged(cls, db, doc, kwargs, source_a, source_b):
        wv = cls(db, kwargs)
        winnow.merge(wv, doc, source_a, source_b)
        db.set(wv.kwargs[u"uuid"], wv.kwargs)
        return wv

    @classmethod
    def patched(cls, db, doc, kwargs, source_a, source_b):
        wv = cls(db, kwargs)
        winnow.patch(wv, doc, source_a, source_b)
        db.set(wv.kwargs[u"uuid"], wv.kwargs)
        return wv

    @classmethod
    def extracted(cls, db, doc, kwargs, source, extractions):
        wv = cls(db, kwargs)
        winnow.extract(wv, doc, source, extractions)
        db.set(wv.kwargs[u"uuid"], wv.kwargs)
        return wv

    @classmethod
    def expanded(cls, db, kwargs, source):
        wv = cls(db, kwargs)
        winnow.expand(wv, source.kwargs[u"doc"], source)
        db.set(wv.kwargs[u"uuid"], wv.kwargs)
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

    def get_uuid(self):
        return self.kwargs[u"uuid"]

    def add_history_action(self, action_name, options_interface):
        history = self.kwargs.get(u"history")
        if history is None:
            history = self.kwargs[u"history"] = []
        history.append([action_name, options_interface.kwargs.get(u"doc_hash")])

    def get_options_dict(self):
        return self.kwargs[u"doc"][u"options"]

    def set_doc(self, doc):
        self.kwargs[u"doc"] = doc

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