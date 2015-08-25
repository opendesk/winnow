from copy import deepcopy
import jsonschema
from decimal import Decimal
import os

from winnow.options import OptionsSet
from winnow import inline
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





def merge(source_a, source_b, target, doc):

    # print "source_a", source_a
    # print "source_b", source_b
    # print "target", target
    # print "doc", doc

    # print source_a, source_b
    doc_b = source_b.get_doc()

    # get the options from bothe sources
    options_a = deepcopy(source_a.get_options_dict())
    options_b = deepcopy(source_b.get_options_dict())

    merged_options = inline._merge_option_dicts(source_a, options_a, options_b)

    # put this merged options into a copy of the doc
    new_doc = deepcopy(doc)
    new_doc[OPTIONS_KEY] = merged_options

    target.clone_history_from(source_a)
    _add_start_if_needed(source_a, target)
    _set_doc(target, new_doc)

    target.add_history_action(action=HISTORY_ACTION_MERGE,
                              input=source_b,
                              output_type=doc.get("type"))


def scope(source, scopes, target, doc):
    new_doc = deepcopy(doc)
    _trim_out_off_scope(new_doc[OPTIONS_KEY], set(scopes))
    target.clone_history_from(source)
    _add_start_if_needed(source, target)
    _set_doc(target, new_doc)

    target.add_history_action(action=HISTORY_ACTION_SCOPE,
                              scope=scopes,
                              output_type=doc.get("type"))


def default_choices(source, scopes):

    #take a copy of the options
    options_dict = deepcopy(source.get_options_dict())

    #expand it
    ref_hashes = {}
    inline.inline_refs(options_dict, source, ref_hashes)

    #scope it
    _trim_out_off_scope(options_dict, set(scopes))

    # wrap it in an options set
    options_set = OptionsSet(options_dict)

    #get default options set
    default = options_set.default()

    return default.store



def quantify(source, target, doc):

    quantity_options = {
        u"quantity": {
            u"type": u"numeric::step",
            u"name": u"Quantity",
            u"default": Decimal("1"),
            u"max": Decimal("10000"),
            u"min": Decimal("1"),
            u"start": Decimal("0"),
            u"step": Decimal("1")
        }
    }

    options_a = OptionsSet(source.get_options_dict())
    options_b = OptionsSet(quantity_options)
    new_doc = deepcopy(doc)
    new_doc[OPTIONS_KEY] = options_a.merge(options_b).store
    target.clone_history_from(source)
    _add_start_if_needed(source, target)
    _set_doc(target, new_doc)

    target.add_history_action(action=HISTORY_ACTION_QUANTIFY,
                              output_type=doc.get("type"))



def _trim_out_off_scope(node, scopes):

    if isinstance(node, dict):
        for key in node.keys():
            child = node[key]
            if isinstance(child, dict):
                if "scopes" in child.keys():
                    child_scopes = set(child["scopes"])
                    if scopes.isdisjoint(child_scopes):
                        del node[key]
                else:
                    _trim_out_off_scope(child, scopes)
            if isinstance(child, list):
                _trim_out_off_scope(child, scopes)

    # recursively trim inside lists
    if isinstance(node, list):
        for i, child in enumerate(node[:]):
            if isinstance(child, dict):
                if "scopes" in child.keys():
                    child_scopes = set(child["scopes"])
                    if scopes.isdisjoint(child_scopes):
                        node.remove(child)
                else:
                    _trim_out_off_scope(child, scopes)
            if isinstance(child, list):
                _trim_out_off_scope(child, scopes)


def filter_allows(filter_source, possible):
    filter_options = OptionsSet(filter_source.get_options_dict())
    return [p for p in possible if filter_options.allows(OptionsSet(p.get_options_dict()))]


def filter_allowed_by(filter_source, possible):
    filter_options = OptionsSet(filter_source.get_options_dict())
    return [p for p in possible if OptionsSet(p.get_options_dict()).allows(filter_options)]


def is_allowed_by(filter_source, possible):
    filter_options = OptionsSet(filter_source.get_options_dict())
    return OptionsSet(possible.get_options_dict()).allows(filter_options)


def expand(source, target):
    new_doc = deepcopy(source.get_doc())
    target.clone_history_from(source)
    ## inline references
    ref_hashes = {}
    inline.inline_refs(new_doc, source, ref_hashes)
    _set_doc(target, new_doc)
    return ref_hashes



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


def asset_props(doc, dl_base=None):
    path = doc.get("path")
    if path is None:
        return []
    relpaths = []
    _walk_dict_for_assets(doc, relpaths)
    return [asset_from_relpath(doc, rp, dl_base=dl_base) for rp in relpaths]

def asset_from_relpath(doc, relpath, dl_base=None):
    if '://' in relpath:
        path = relpath
    else:
        path = os.path.normpath("%s/%s" % (doc['path'], relpath))
    return {
        "path": path,
        "source": doc['source'],
        "base": doc.get("base", dl_base),
        "relpath": relpath,
    }

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
    except jsonschema.ValidationError, e:
        raise OptionsExceptionFailedValidation(e)


def _set_doc(target, doc):
    validate(doc)
    target.set_doc(doc)
    target.set_doc_hash(utils.get_doc_hash(utils.json_dumps(doc)))
