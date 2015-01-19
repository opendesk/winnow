from copy import deepcopy
from jsonschema import validate, ValidationError

from sieve.utils import get_doc_hash, json_dumps
from schemas import SIEVE_SCHEMA
from sieve.options_set import OptionsSet
from sieve.product_exceptions import ProductExceptionFailedValidation

OPTIONS_KEY = u"options"

HISTORY_ACTION_START = u"start"
HISTORY_ACTION_MERGE = u"merge"
HISTORY_ACTION_PATCH = u"patch"


class OptionsDelegate(object):

    def set_is_snapshot(self):
        pass

    def set_doc_hash(self, hash):
        pass

    def add_history_action(self, action_name, sieve_delegate):
        pass

    def get_options_dict(self):
        pass

    def set_doc(self, doc):
        pass

    def get_doc(self):
        pass

    def clone_history_from(self, sieve_delegate):
        pass

    def clone(self):
        """return a clone"""
        pass

    def get_upstream(self):
        """
        returns the upstream delegate
        """


def start(delegate, doc):
    _set_doc(delegate, doc)
    delegate.add_history_action(HISTORY_ACTION_START, delegate)


def merge(delegate, doc, source_delegate, input_delegate):
    source_options = OptionsSet(source_delegate.get_options_dict())
    input_options = OptionsSet(input_delegate.get_options_dict())
    doc[OPTIONS_KEY] = source_options.merge(input_options).store
    delegate.clone_history_from(source_delegate)
    _set_doc(delegate, doc)
    delegate.add_history_action(HISTORY_ACTION_MERGE, input_delegate)


def patch(delegate, doc, source_delegate, input_delegate):
    source_options = OptionsSet(source_delegate.get_options_dict())
    input_options = OptionsSet(input_delegate.get_options_dict())
    doc[OPTIONS_KEY] = source_options.patch(input_options).store
    delegate.clone_history_from(source_delegate)
    _set_doc(delegate, doc)
    delegate.add_history_action(HISTORY_ACTION_PATCH, input_delegate)


def extract(delegate, doc, source_delegate, extractions):
    source_options = OptionsSet(source_delegate.get_options_dict())
    doc[OPTIONS_KEY] = source_options.extract(extractions).store
    delegate.clone_history_from(source_delegate)
    _set_doc(delegate, doc)
    delegate.add_history_action(HISTORY_ACTION_PATCH, extractions)


def take_snapshot(source_delegate):
    patched = _patch_upstream(source_delegate)
    patched.set_is_snapshot()
    return patched


def _set_doc(delegate, doc):
    try:
        validate(doc, SIEVE_SCHEMA)
    except ValidationError, e:
        raise ProductExceptionFailedValidation(e)
    delegate.set_doc(deepcopy(doc))
    delegate.set_doc_hash(get_doc_hash(json_dumps(doc)))


def _patch_upstream(source_delegate):
    upstream_delegate = source_delegate.get_upstream()
    if upstream_delegate is None:
        return source_delegate
    patched_delegate = source_delegate.clone()
    patch(patched_delegate, source_delegate.get_doc(), source_delegate, upstream_delegate)
    patched_delegate = _patch_upstream(patched_delegate)
    return patched_delegate




