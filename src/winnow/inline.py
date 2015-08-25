from copy import deepcopy
from winnow import utils
from winnow.exceptions import OptionsExceptionReferenceError
from winnow.options import OptionsSet


def _lookup_and_hash_ref(reference, source, options, node, ref_hashes):
    found = _find_expanded_ref(reference, source, options, ref_hashes)
    expanded_hash = utils.get_doc_hash(utils.json_dumps(found))
    ref_hashes[expanded_hash] = node
    return found

def _merge_option_dicts(source, options_a, options_b):

    # expand the options dicts collecting their replaced refs
    ref_hashes = {}
    inline_refs(options_a, source, ref_hashes)
    inline_refs(options_b, source, ref_hashes)

    # do the merge
    set_a = OptionsSet(options_a)
    set_b = OptionsSet(options_b)

    merged_options = set_a.merge(set_b).store
    # un merge unchanged refs by looking at the ref_hashes
    restore_unchanged_refs(merged_options, ref_hashes)

    return merged_options

def _find_expanded_ref(reference, source, options, ref_hashes):

    # looks up the contents of a reference
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

                referenced_doc[u"options"] = _merge_option_dicts(source, options_a.store, options_b.store)

        new_doc = _extract_internal_path(referenced_doc, internal_path) if internal_path else referenced_doc
        inline_refs(new_doc, source, ref_hashes, )
        return new_doc




def restore_unchanged_refs(node, ref_hashes):
    # walks the node and restores any value that matches one in the ref_hashes

    if isinstance(node, dict):
        for key, child in node.iteritems():
            hash = utils.get_doc_hash(utils.json_dumps(child))
            if hash in ref_hashes.keys():
                node[key] = ref_hashes[hash]
            elif isinstance(child, dict):
                restore_unchanged_refs(child, ref_hashes)
            if isinstance(child, list):
                restore_unchanged_refs(child, ref_hashes)
    if isinstance(node, list):
        for i, child in enumerate(node[:]):
            hash = utils.get_doc_hash(utils.json_dumps(child))
            if hash in ref_hashes.keys():
                node[i] = ref_hashes[hash]
            elif isinstance(child, dict):
                restore_unchanged_refs(child, ref_hashes)
            if isinstance(child, list):
                restore_unchanged_refs(child, ref_hashes)


def inline_refs(node, source, ref_hashes):

    # walks list and dicts looking for refs

    if isinstance(node, dict):
        for key, child in node.iteritems():
            if isinstance(child, dict):
                if u"$ref" in child.keys():
                    node[key] = _lookup_and_hash_ref(child[u"$ref"], source, child.get(u"options"), child, ref_hashes)
                else:
                    inline_refs(child, source, ref_hashes)
            if isinstance(child, unicode):
                if child.startswith(u"$ref:"):
                    node[key] = _lookup_and_hash_ref(child[len(u"$ref:"):], source, None, child, ref_hashes)
            if isinstance(child, list):
                inline_refs(child, source, ref_hashes)
    if isinstance(node, list):
        for i, child in enumerate(node[:]):
            if isinstance(child, dict):
                if u"$ref" in child.keys():
                    node[i] = _lookup_and_hash_ref(child[u"$ref"], source, child.get(u"options"), child, ref_hashes)
                else:
                    inline_refs(child, source, ref_hashes)
            if isinstance(child, unicode):
                if child.startswith(u"$ref:"):
                    node[i] = _lookup_and_hash_ref(child[len(u"$ref:"):], source, None, child, ref_hashes)
            if isinstance(child, list):
                inline_refs(child, source, ref_hashes)


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


