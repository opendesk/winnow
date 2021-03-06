from winnow.utils import deep_copy_dict as deepcopy
import winnow

# from winnow.munge import remove_key_named

from winnow.models.product import WinnowProduct
from winnow.models.fileset import WinnowFileset
from winnow.models.process import WinnowProcess
from winnow.models.material import WinnowMaterial
from winnow.models.finish import WinnowFinish
from winnow.models.base import WinnowVersion
from winnow.models.namespace import WinnowNamespace
from winnow.models.licence import WinnowLicence
from winnow.models.quantified_configuration import WinnowQuantifiedConfiguration

FACTORY_LOOKUP = {
    "license": WinnowLicence,
    "namespace": WinnowNamespace,
    "range" : WinnowVersion,
    "design" : WinnowVersion,
    "process" : WinnowProcess,
    "material" : WinnowMaterial,
    "finish" : WinnowFinish,
    "product" : WinnowProduct,
    "fileset" : WinnowFileset,
    "context" : WinnowVersion,
    "choice" : WinnowVersion,
    "size" : WinnowVersion,
    "contextualised_product" : WinnowVersion,
    "quantified_configuration" : WinnowQuantifiedConfiguration,
}


def publish(db, as_json):
    try:
        cls = FACTORY_LOOKUP[as_json[u"type"]]
    except KeyError, e:
        print as_json
        raise e
    return cls.publish(db, as_json)


def get_customer_contexts(session_id):

    return []

def get_maker_contexts(maker_id):

    return []


def get_default_product_options(db, product_path, session_id):

    context_paths = get_customer_contexts(session_id)
    product = WinnowProduct.get_from_path(db, product_path)

    expanded = product.expanded() # no need to save this

    for context_path in context_paths:
        context = WinnowVersion.get_from_path(db, context_path)
        expanded = expanded.merged(context)

    scoped = expanded.scoped(u"customer")
    quantified = scoped.quantified()

    return quantified





def get_quantified_configuration(db, product_path, choices):

    doc = {
        "schema": "https://opendesk.cc/schemata/options.json",
        "type": "choice",
        "name": "paul's choices",
        "options":choices
    }

    choice_document = WinnowVersion.add_doc(db, doc)

    product = WinnowProduct.get_from_path(db, product_path)

    qc_doc = deepcopy(product.get_doc())
    product_doc = product.get_doc()

    version = product_doc["version"]

    qc_doc[u"type"] = "quantified_configuration"
    qc_doc[u"schema"] = "https://opendesk.cc/schemata/options.json"
    qc_doc[u"product"] = "%s@%s.%s.%s" % (product_doc["path"], version[0], version[1], version[2])

    return WinnowQuantifiedConfiguration.merged(db, qc_doc, {}, product, choice_document)


def get_filesets_for_quantified_configuration(db, quantified_configuration):

    qc_doc = quantified_configuration.get_doc()

    product_path = qc_doc["product"].split("@")[0]
    product = WinnowProduct.get_from_path(db, product_path)

    filesets = product.get_filesets(db)

    matching = winnow.filter_allowed_by(quantified_configuration, filesets)

    self_keys = set(qc_doc[u"options"].keys())

    found = []

    for match in matching:
        other_keys = set(match.get_doc()[u"options"].keys())
        matched = self_keys.intersection(other_keys)
        fs = {"fileset": match,
              "matched": matched,
              "unmatched": other_keys.difference(matched)
              }
        found.append(fs)

    def best_match(x, y):
        return len(y["matched"]) - len(x["matched"])

    sorted_found = sorted(found, cmp=best_match)

    return sorted_found

    # return quantified_configuration.get_filesets(db)
    #



def get_manufacturing_spec(db, quantified_configuration, fileset):

    qc_doc = quantified_configuration.get_doc()
    fs_doc = fileset.get_doc()

    ms_doc = {}
    ms_doc[u"product"] = qc_doc[u"product"]
    ms_doc[u"type"] = u"manufacturing_spec"
    ms_doc[u"schema"] = u"https://opendesk.cc/schemata/options.json"
    ms_doc[u"fileset"] = fs_doc[u"path"]
    ms_doc[u"manufacturing"] = fs_doc[u"manufacturing"]
    ms_doc[u"files"] = fs_doc[u"files"]

    spec = WinnowQuantifiedConfiguration.merged(db, ms_doc, {}, fileset, quantified_configuration)

    return spec


# def coerce_material_to_most_specific(options):
#
#     # find material ref in material-choices
#
#     gatherer = {}
#
#     optionscopy = deepcopy(options)
#
#     remove_key_named(optionscopy["material-choices"], "material", gatherer)
#
#     material_values = gatherer["material"]["values"]
#
#     if len(material_values) == 1:
#         ref = material_values[0]["path"]
#
#         print "*************** FOUND ************", ref





def get_manufacturing_choices(db, manufacturing_spec, maker_id):

    context_paths = get_maker_contexts(maker_id)
    merged = manufacturing_spec

    for context_path in context_paths:
        context = WinnowVersion.get_from_path(db, context_path)
        merged = merged.merged(context)

    scoped = merged.scoped([u"maker"])
    return scoped



