import winnow
from winnow.interface import OptionsInterface
from copy import deepcopy
from winnow.constants import *


class WinnowVersion(OptionsInterface):

    def __init__(self, db, kwargs):
        self.kwargs = deepcopy(kwargs)
        self.db = db

    ##  oo wrappers around winnow operations

    @classmethod
    def create(cls, db, doc, kwargs):
        wv = cls(db, kwargs)
        winnow.create(wv, doc)
        db.set(wv, wv.kwargs[u"doc_hash"])
        return wv

    @classmethod
    def merged(cls, db, doc, kwargs, source_a, source_b):
        wv = cls(db, kwargs)
        winnow.merge(wv, doc, source_a, source_b)
        db.set(wv, wv.kwargs[u"doc_hash"])
        return wv

    @classmethod
    def patched(cls, db, doc, kwargs, source_a, source_b):
        wv = cls(db, kwargs)
        winnow.patch(wv, doc, source_a, source_b)
        db.set(wv, wv.kwargs[u"doc_hash"])
        return wv

    @classmethod
    def extracted(cls, db, doc, kwargs, source, extractions):
        wv = cls(db, kwargs)
        winnow.extract(wv, doc, source, extractions)
        db.set(wv, wv.kwargs[u"doc_hash"])
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

    def set_is_snapshot(self):
        self.kwargs[u"is_snapshot"] = True

    def set_doc_hash(self, hash):
        self.kwargs[u"doc_hash"] = hash

    def add_history_action(self, action_name, options_interface):
        history = self.kwargs.get(u"history")
        if history is None:
            history = self.kwargs[u"history"] = []
        history.append([action_name, options_interface.kwargs.get(u"doc_hash")])

    def add_history_extractions(self, extractions):
        history = self.kwargs.get(u"history")
        if history is None:
            history = self.kwargs[u"history"] = []
        history.append([HISTORY_ACTION_EXTRACT, extractions])

    def get_options_dict(self):
        return self.kwargs[u"doc"][u"options"]

    def set_doc(self, doc):
        self.kwargs[u"doc"] = doc

    def get_doc(self):
        return self.kwargs.get(u"doc")

    def clone_history_from(self, options_interface):
        self.kwargs[u"history"] = deepcopy(options_interface.kwargs[u"history"])

    def clone(self):
        return self.__class__(self.db, self.kwargs)

    def get_upstream(self):
        upstream_id = self.kwargs[u"doc"].get(u"upstream")
        if upstream_id is None:
            return None
        else:
            kwargs = self.db.get(upstream_id)
            return WinnowVersion(self.db, kwargs)
