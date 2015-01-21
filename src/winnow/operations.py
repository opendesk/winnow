from copy import deepcopy
from jsonschema import validate, ValidationError

from winnow.options import OptionsSet
from winnow import utils
from winnow import schemas
from winnow.exceptions import OptionsExceptionFailedValidation
from winnow.constants import *


def add_doc(target, doc):
    _set_doc(target,  deepcopy(doc))


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
    _add_start_if_needed(target, source_a)
    _set_doc(target, new_doc)
    target.add_history_action(HISTORY_ACTION_MERGE, source_b)


def patch(target, doc, source_a, source_b):
    options_a = OptionsSet(source_a.get_options_dict())
    options_b = OptionsSet(source_b.get_options_dict())
    new_doc = deepcopy(doc)
    new_doc[OPTIONS_KEY] = options_a.patch(options_b).store
    target.clone_history_from(source_a)
    _add_start_if_needed(target, source_a)
    _set_doc(target, new_doc)
    target.add_history_action(HISTORY_ACTION_PATCH, source_b)


def extract(target, doc, source, extractions):
    options = OptionsSet(source.get_options_dict())
    new_doc = deepcopy(doc)
    keys_to_extract = extractions.get_options_dict().keys()
    new_doc[OPTIONS_KEY] = options.extract(keys_to_extract).store
    target.clone_history_from(source)
    _add_start_if_needed(target, source)
    _set_doc(target, new_doc)
    target.add_history_action(HISTORY_ACTION_EXTRACT, extractions)


def filter_allows(filter_source, possible):
    filter_options = OptionsSet(filter_source.get_options_dict())
    return [p for p in possible if filter_options.allows(OptionsSet(p.get_options_dict()))]


def filter_allowed_by(filter_source, possible):
    filter_options = OptionsSet(filter_source.get_options_dict())
    return [p for p in possible if OptionsSet(p.get_options_dict()).allows(filter_options)]


def expand(target, doc, source):
    options = OptionsSet(source.get_options_dict())
    new_doc = deepcopy(doc)
    target.clone_history_from(source)
    new_doc[OPTIONS_KEY] = _patch_upstream(target, source, options).store
    _set_doc(target, new_doc)
    target.set_is_expanded()


def _patch_upstream(target, source, options_set):

    upstream_delegate = source.get_upstream()
    if not upstream_delegate:
        return options_set

    upstream_options = OptionsSet(upstream_delegate.get_options_dict())
    patched_options_set = options_set.patch(upstream_options)
    _add_start_if_needed(target, source)
    target.add_history_action(HISTORY_ACTION_PATCH, upstream_delegate)
    return _patch_upstream(target, upstream_delegate, patched_options_set)


def _add_start_if_needed(target, source):
    if target.history_is_empty():
        target.add_history_action(HISTORY_ACTION_START, source)


def validate_doc(doc, type_name=None):
    try:
        validate(doc, schemas.BASE)
    except ValidationError, e:
        raise OptionsExceptionFailedValidation(e)
    if type_name is not None:
        try:

            validate(doc, )
        except ValidationError, e:
            raise OptionsExceptionFailedValidation(e)


def _set_doc(target, doc):
    validate_doc(doc)
    target.set_doc(doc)
    target.set_doc_hash(utils.get_doc_hash(utils.json_dumps(doc)))
