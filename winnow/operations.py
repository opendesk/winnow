from copy import deepcopy
from jsonschema import validate, ValidationError

from winnow.options import OptionsSet
from winnow.utils import get_doc_hash, json_dumps
from winnow.schemas import SIEVE_SCHEMA
from winnow.exceptions import OptionsExceptionFailedValidation
from winnow.constants import *


def create(target, doc):
    _set_doc(target,  deepcopy(doc))
    target.add_history_action(HISTORY_ACTION_CREATE, target)


def allows(source_a, source_b):
    options_a = OptionsSet(source_a.get_options_dict())
    options_b = OptionsSet(source_b.get_options_dict())
    return options_a.allows(options_b)


def intersects(source_a, source_b):
    options_a = OptionsSet(source_a.get_options_dict())
    options_b = OptionsSet(source_b.get_options_dict())
    return options_a.intersects(options_b)


def merge(target, doc, source_a, source_b):
    options_a = OptionsSet(source_a.get_options_dict())
    options_b = OptionsSet(source_b.get_options_dict())
    new_doc = deepcopy(doc)
    new_doc[OPTIONS_KEY] = options_a.merge(options_b).store
    target.clone_history_from(source_a)
    _set_doc(target, new_doc)
    target.add_history_action(HISTORY_ACTION_MERGE, source_b)


def patch(target, doc, source_a, source_b):
    options_a = OptionsSet(source_a.get_options_dict())
    options_b = OptionsSet(source_b.get_options_dict())
    new_doc = deepcopy(doc)
    new_doc[OPTIONS_KEY] = options_a.patch(options_b).store
    target.clone_history_from(source_a)
    _set_doc(target, new_doc)
    target.add_history_action(HISTORY_ACTION_PATCH, source_b)


def extract(target, doc, source, extractions):
    options = OptionsSet(source.get_options_dict())
    new_doc = deepcopy(doc)
    new_doc[OPTIONS_KEY] = options.extract(extractions).store
    target.clone_history_from(source)
    _set_doc(target, new_doc)
    target.add_history_extractions(extractions)


def filter_allows(filter, possible):

    filter_options = OptionsSet(filter.get_options_dict())
    return [p for p in possible if filter_options.allows(OptionsSet(p.get_options_dict()))]


def filter_allowed_by(filter, possible):

    filter_options = OptionsSet(filter.get_options_dict())
    return [p for p in possible if OptionsSet(p.get_options_dict()).allows(filter_options)]


def take_snapshot(source):
    patched = _patch_upstream(source)
    patched.set_is_snapshot()
    return patched


def _set_doc(target, doc):
    try:
        validate(doc, SIEVE_SCHEMA)
    except ValidationError, e:
        raise OptionsExceptionFailedValidation(e)
    target.set_doc(doc)
    target.set_doc_hash(get_doc_hash(json_dumps(doc)))


def _patch_upstream(source):
    upstream_delegate = source.get_upstream()
    if upstream_delegate is None:
        return source
    patched_delegate = source.clone()
    patch(patched_delegate, source.get_doc(), source, upstream_delegate)
    patched_delegate = _patch_upstream(patched_delegate)
    return patched_delegate