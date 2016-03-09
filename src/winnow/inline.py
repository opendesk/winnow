from winnow.utils import deep_copy_dict as deepcopy
from winnow import utils
from winnow.exceptions import OptionsExceptionReferenceError, OptionsExceptionSetWithException, OptionsExceptionEmptyOptionValues
from winnow.options import OptionsSet


def _lookup_and_hash_ref(reference, doc, source, options, node, ref_hashes, default_scopes=None):

    found = _find_expanded_ref(reference, doc, source, options, ref_hashes, default_scopes=default_scopes)
    # this ensures than only external references are unexpanded
    if not(reference.startswith(u"~") or reference.startswith(u"#")):
        expanded_hash = utils.get_doc_hash(utils.json_dumps(found))
        ref_hashes[expanded_hash] = node

    return found


def _merge_option_dicts(source, options_a, options_b, ref_doc_a, ref_doc_b, errors=[]):

    # expand the options dicts collecting their replaced refs
    ref_hashes = {}

    inline_refs(options_a, ref_doc_a, source, ref_hashes)
    inline_refs(options_b, ref_doc_b, source, ref_hashes)

    # do the merge
    set_a = OptionsSet(options_a)
    set_b = OptionsSet(options_b)

    try:
        merged_options = set_a.merge(set_b).store
    except OptionsExceptionSetWithException as e:
        merged_options = e.set.store
        for ex_info in e.exception_infos:
            key = ex_info[0]
            values = ex_info[1]

            msg = """***** Merge Error ****

Merging:

type: {type_a}
path: {path_a}

with

type: {type_b}
path: {path_b}

Gave an empty result for the key: {key}

When using these values:
{values}
        """.format(type_a=ref_doc_a.get("type"),
                   type_b=ref_doc_b.get("type"),
                   path_a=ref_doc_a.get("path"),
                   path_b=ref_doc_b.get("path"),
                   key=key,
                   values = "\n".join([utils.json_dumps(v.as_json()) for v in values])
                   )

            errors.append(msg)

    # un merge unchanged refs by looking at the ref_hashes
    restore_unchanged_refs(merged_options, ref_hashes)

    return merged_options



def get_inlined_options(source):

    ref_doc = source.get_doc()
    # expand all the refs
    ref_hashes = {}
    inlined = deepcopy(ref_doc["options"])
    inline_refs(inlined, ref_doc, source, ref_hashes)
    return inlined




def _find_expanded_ref(reference, doc, source, options, ref_hashes, default_scopes=None):


    # looks up the contents of a reference


    if u"~" in reference:
        ref, internal_path = reference.split(u"~")
    elif u"#" in reference:
        ref, internal_path = reference.split(u"#")
    else:
        ref = reference
        internal_path = None
    if ref == "":
        referenced_doc = doc
    else:
        wv = source.lookup(ref)
        if wv is None:
            raise OptionsExceptionReferenceError("Winnow Reference Error: Failed to find resource %s" % ref)
        existing_doc = wv.get_doc()
        referenced_doc = deepcopy(existing_doc)
    if referenced_doc is None:
        raise OptionsExceptionReferenceError("Winnow Reference Error: Cannot find reference %s as ref doc is None" % ref)
    else:
        if options is not None:
            # if the ref also has some options then pre merge them into the reference
            referenced_options = referenced_doc.get(u"options")
            if referenced_options is None:
                referenced_doc[u"options"] = options
            else:
                options_a = OptionsSet(referenced_options)
                options_b = OptionsSet(options)
                referenced_doc[u"options"] = _merge_option_dicts(source, options_a.store, options_b.store, referenced_doc, doc)

            ## TODO look again at the the default scopes thing
            # if default_scopes is not None:
            #     for k, v in referenced_doc[u"options"].iteritems():
            #         print v
            #         if v.get("scopes") is None:
            #             v["scopes"] = default_scopes

        new_doc = _extract_internal_path(referenced_doc, internal_path) if internal_path else referenced_doc
        # TODO revisit this use of doc as the reference doc to use
        new_doc = inline_refs(new_doc, doc, source, ref_hashes)
        return new_doc

def restore_unchanged_refs(node, ref_hashes):
    # walks the node and restores any value that matches one in the ref_hashes

    if isinstance(node, dict):
        for key, child in node.iteritems():
            hash = utils.get_doc_hash(utils.json_dumps(child))
            # if key.endswith("material"):
            #     print "restore", key, hash
            #     print "-------------------------"
            #     options = child.get("options")
            #     if "thickness" in options.keys():
            #         print options["thickness"]
                # print utils.json_dumps(child)
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


def inline_refs(node, doc, source, ref_hashes):

    # walks list and dicts looking for refs


    if isinstance(node, dict) and u"$ref" in node.keys():
        new_node = _lookup_and_hash_ref(node[u"$ref"], doc, source, node.get(u"options"), node, ref_hashes)
        return new_node

    elif isinstance(node, dict):
        for key, child in node.iteritems():
            if isinstance(child, dict):
                if u"$ref" in child.keys():
                    node[key] = _lookup_and_hash_ref(child[u"$ref"],
                                                     doc,
                                                     source,
                                                     child.get(u"options"),
                                                     child,
                                                     ref_hashes,
                                                     default_scopes=child.get(u"scopes"))
                else:
                    inline_refs(child, doc, source, ref_hashes)
            if isinstance(child, unicode):
                if child.startswith(u"$ref:"):
                    node[key] = _lookup_and_hash_ref(child[len(u"$ref:"):], doc, source, None, child, ref_hashes)
            if isinstance(child, list):
                inline_refs(child, doc, source, ref_hashes)
    if isinstance(node, list):
        for i, child in enumerate(node[:]):
            if isinstance(child, dict):
                if u"$ref" in child.keys():
                    node[i] = _lookup_and_hash_ref(child[u"$ref"],
                                                   doc,
                                                   source,
                                                   child.get(u"options"),
                                                   child,
                                                   ref_hashes,
                                                   default_scopes=child.get(u"scopes"))
                else:
                    inline_refs(child, doc, source, ref_hashes)
            if isinstance(child, str):
                if not "Merge Error" in child:
                    raise Exception("we shouldnt be getting a string in inline_refs {}".format(child))
            if isinstance(child, unicode):
                if child.startswith(u"$ref:"):
                    node[i] = _lookup_and_hash_ref(child[len(u"$ref:"):], doc, source, None, child, ref_hashes)
            if isinstance(child, list):
                inline_refs(child, doc, source, ref_hashes)

    return node


def _extract_internal_path(doc, path):
    walker = doc
    parts = [p for p in path.split("/") if p]
    for part in parts:
        if not isinstance(walker, dict):
            raise OptionsExceptionReferenceError("internal_path reference couldn't find %s in %s" % (path, doc))
        walker = walker.get(part)
        if walker is None:
            raise OptionsExceptionReferenceError("internal_path reference couldn't find %s in %s" % (path, doc))
    return deepcopy(walker)


