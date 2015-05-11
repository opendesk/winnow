from copy import deepcopy
from jsonschema import validate, ValidationError

from winnow.options import OptionsSet
from winnow import utils
from winnow import validation
from winnow.exceptions import OptionsExceptionFailedValidation, OptionsExceptionReferenceError
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


def merge(source_a, source_b, target, doc):
    doc_b = source_b.get_doc()
    options_a = OptionsSet(source_a.get_options_dict())
    options_b = OptionsSet(source_b.get_options_dict())
    new_doc = deepcopy(doc)
    new_doc[OPTIONS_KEY] = options_a.merge(options_b).store
    target.clone_history_from(source_a)
    _add_start_if_needed(source_a, target)
    _set_doc(target, new_doc)

    target.add_history_action(action=HISTORY_ACTION_MERGE,
                              input=source_b,
                              output_type=doc.get("type"))


def patch(source_a, source_b, target, doc):
    doc_b = source_b.get_doc()
    options_a = OptionsSet(source_a.get_options_dict())
    options_b = OptionsSet(source_b.get_options_dict())
    new_doc = deepcopy(doc)
    new_doc[OPTIONS_KEY] = options_a.patch(options_b).store
    target.clone_history_from(source_a)
    _add_start_if_needed(source_a, target)
    _set_doc(target, new_doc)

    target.add_history_action(action=HISTORY_ACTION_PATCH,
                              input=source_b,
                              output_type=doc.get("type"))


def scope(source, scope, target, doc):
    options = OptionsSet(source.get_options_dict())
    new_doc = deepcopy(doc)
    new_doc[OPTIONS_KEY] = options.scope(scope).store
    target.clone_history_from(source)
    _add_start_if_needed(source, target)
    _set_doc(target, new_doc)

    target.add_history_action(action=HISTORY_ACTION_SCOPE,
                              scope=scope,
                              output_type=doc.get("type"))


def filter_allows(filter_source, possible):
    filter_options = OptionsSet(filter_source.get_options_dict())
    return [p for p in possible if filter_options.allows(OptionsSet(p.get_options_dict()))]


def filter_allowed_by(filter_source, possible):
    filter_options = OptionsSet(filter_source.get_options_dict())
    return [p for p in possible if OptionsSet(p.get_options_dict()).allows(filter_options)]


def inline(source, target):
    new_doc = deepcopy(source.get_doc())
    target.clone_history_from(source)
    ## inline references
    options_dict = new_doc[OPTIONS_KEY]
    _inline_option_refs(options_dict, source)
    _set_doc(target, new_doc)


def expand(source, target):
    options = OptionsSet(source.get_options_dict())
    new_doc = deepcopy(source.get_doc())
    target.clone_history_from(source)
    ## expand upstream inheritance
    new_doc[OPTIONS_KEY] = _patch_upstream(source, target, options).store
    _set_doc(target, new_doc)
    target.set_is_expanded()


def _inline_option_refs(node, source):

    # walks list and dicts looking for dicts with ref key
    #
    if isinstance(node, dict):
        if u"type" in node.keys() and node[u"type"] == u"set::resource":
            if u"values" in node.keys():
                values = node[u"values"]
                if type(values) == list:
                    node[u"values"] = [_expand_doc_inplace(source.get_ref(ref)) for ref in values]
                elif type(values) == unicode:
                    node[u"values"] = _expand_doc_inplace(source.get_ref(values))
                else:
                    pass
        else:
            for k, v in node.iteritems():
                _inline_option_refs(v, source)
    if isinstance(node, list):
        for v in node:
            _inline_option_refs(v, source)


def _expand_doc_inplace(source):
    print "source", type(source)
    options = OptionsSet(source.get_options_dict())
    new_doc = deepcopy(source.get_doc())
    ## expand upstream inheritance
    new_doc[OPTIONS_KEY] = _patch_upstream(source, None, options).store
    return new_doc




def _patch_upstream(source, target, options_set):

    doc = source.get_doc()
    if u"upstream" in doc.keys():
        upstream_delegate = source.get_upstream()
        if upstream_delegate is None:
            raise OptionsExceptionReferenceError("Winnow Reference Error: Cannot find upstream reference %s" % doc[u"upstream"])
    else:
        return options_set

    upstream_options = OptionsSet(upstream_delegate.get_options_dict())
    patched_options_set = options_set.patch(upstream_options)
    if target is not None:
        _add_start_if_needed(source, target)
        target.add_history_action(action=HISTORY_ACTION_PATCH,
                              input=upstream_delegate,
                              output_type=doc.get("type"))

    return _patch_upstream(upstream_delegate, target, patched_options_set)


def _add_start_if_needed(source, target):
    if target.history_is_empty():
        doc = source.get_doc()

        target.add_history_action(action=HISTORY_ACTION_START,
                              input=source,
                              output_type=doc.get("type"))


def asset_paths(doc):
    path = doc.get("path")
    if path is None:
        return []
    found = []
    _walk_dict_for_assets(doc, found)
    return found


def _walk_dict_for_assets(node, found):

    if isinstance(node, dict):
        if u"asset" in node.keys():
            found.append(node[u"asset"])
        else:
            for k, v in node.iteritems():
                _walk_dict_for_assets(v, found)
    if isinstance(node, list):
        for v in node:
            _walk_dict_for_assets(v, found)


def validate(doc):
    try:
        validation.validate(doc)
    except ValidationError, e:
        raise OptionsExceptionFailedValidation(e)


def _set_doc(target, doc):
    validate(doc)
    target.set_doc(doc)
    target.set_doc_hash(utils.get_doc_hash(utils.json_dumps(doc)))
