from copy import deepcopy
import jsonschema
from decimal import Decimal
import os

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


def scope(source, scopes, target, doc):
    new_doc = deepcopy(doc)
    _trim_out_off_scope(new_doc[OPTIONS_KEY], set(scopes))
    target.clone_history_from(source)
    _add_start_if_needed(source, target)
    _set_doc(target, new_doc)

    target.add_history_action(action=HISTORY_ACTION_SCOPE,
                              scope=scopes,
                              output_type=doc.get("type"))


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


def expand(source, target):
    new_doc = deepcopy(source.get_doc())
    target.clone_history_from(source)
    ## inline references
    _inline_refs(new_doc, source)
    _set_doc(target, new_doc)


def _extract_internal_path(doc, path):
    walker = doc
    parts = [p for p in path.split("/") if p]
    for part in parts:
        if not isinstance(walker, dict):
            raise OptionsExceptionReferenceError("internal_path reference couldn't find %s in %s" % (path, doc))
        walker = walker.get(part)
        if walker is None:
            raise OptionsExceptionReferenceError("internal_path reference couldn't find %s in %s" % (path, doc))
    return walker


def _expanded_ref(reference, source, options):

    if u"~" in reference:
        ref, internal_path = reference.split(u"~")
    else:
        ref = reference
        internal_path = None
    if ref == "":
        referenced_doc = source.get_doc()
    else:
        wv = source.lookup(ref)
        if wv is None:
            raise OptionsExceptionReferenceError("Winnow Reference Error: Cannot find reference %s in %s" % (ref, source.get_doc()[u"path"]))
        doc = wv.get_doc()
        referenced_doc = deepcopy(doc)

    if referenced_doc is None:
        return None
    else:
        if options is not None:
            # if the ref also has some options then pre merge them into the reference
            referenced_options = referenced_doc.get(u"options")
            if referenced_options is None:
                referenced_doc[u"options"] = options
            else:
                options_a = OptionsSet(referenced_options)
                options_b = OptionsSet(options)
                referenced_doc[u"options"] = options_a.merge(options_b).store

        # now if there is an internal_path try to pull this out
        new_doc = _extract_internal_path(referenced_doc, internal_path) if internal_path else referenced_doc
        _inline_refs(new_doc, source)
        return new_doc


def _inline_refs(node, source):

    # walks list and dicts looking for refs
    # will may break due to inplace editing during iteration of dict
    #

    if isinstance(node, dict):
        for key, child in node.iteritems():
            if isinstance(child, dict):
                if u"$ref" in child.keys():
                    node[key] = _expanded_ref(child[u"$ref"], source, child.get(u"options"))
                else:
                    _inline_refs(child, source)
            if isinstance(child, unicode):
                if child.startswith(u"$ref:"):
                    node[key] = _expanded_ref(child[len(u"$ref:"):], source, None)
            if isinstance(child, list):
                _inline_refs(child, source)
    if isinstance(node, list):
        for i, child in enumerate(node[:]):
            if isinstance(child, dict):
                if u"$ref" in child.keys():
                    node[i] = _expanded_ref(child[u"$ref"], source, child.get(u"options"))
                else:
                    _inline_refs(child, source)
            if isinstance(child, unicode):
                if child.startswith(u"$ref:"):
                    node[i] = _expanded_ref(child[len(u"$ref:"):], source, None)
            if isinstance(child, list):
                _inline_refs(child, source)


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

def asset_paths(doc, dl_base=None):
    path = doc.get("path")
    if path is None:
        return []
    found = []
    _walk_dict_for_assets(doc, found)
    paths = []
    for asset_relpath in found:
        base = doc.get("base") if doc.get("base") else dl_base
        paths.append({
            "source": doc["source"],
            "base": base,
            "path": os.path.normpath("%s/%s" % (doc.get(u"path"), asset_relpath)),
            "relpath": asset_relpath
        })
    return paths



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
