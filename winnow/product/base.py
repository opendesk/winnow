import winnow
from winnow.options_interface import OptionsInterface


from copy import deepcopy



class WinnowVersion(OptionsInterface):

    def __init__(self, db, kwargs):
        self.kwargs = deepcopy(kwargs)
        self.db = db

    @classmethod
    def create(cls, db, doc, kwargs):
        wv = cls(db, kwargs)
        winnow.create(wv, doc)
        db.set(wv, wv.kwargs[u"doc_hash"])
        return wv

    def set_is_snapshot(self):
        self.kwargs[u"is_snapshot"] = True

    def set_doc_hash(self, hash):
        self.kwargs[u"doc_hash"] = hash

    def add_history_action(self, action_name, sieve_delegate):
        history = self.kwargs.get(u"history")
        if history is None:
            history = self.kwargs[u"history"] = []
        history.append([action_name, sieve_delegate.kwargs.get(u"doc_hash")])

    def get_options_dict(self):
        return self.kwargs[u"doc"][u"options"]

    def set_doc(self, doc):
        self.kwargs[u"doc"] = doc

    def get_doc(self):
        return self.kwargs.get(u"doc")

    def clone_history_from(self, sieve_delegate):
        self.kwargs[u"history"] = deepcopy(sieve_delegate.kwargs[u"history"])

    def clone(self):
        return self.__class__(self.db, self.kwargs)

    def get_upstream(self):
        upstream_id = self.kwargs[u"doc"].get(u"upstream")
        if upstream_id is None:
            return None
        else:
            kwargs = self.db.get(upstream_id)
            return WinnowVersion(self.db, kwargs)
