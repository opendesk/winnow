from copy import deepcopy
import winnow

from winnow.models.product import WinnowProduct
from winnow.models.fileset import WinnowFileset
from winnow.models.process import WinnowProcess
from winnow.models.material import WinnowMaterial
from winnow.models.finish import WinnowFinish
from winnow.models.base import WinnowVersion
from winnow.models.quantified_configuration import WinnowQuantifiedConfiguration

FACTORY_LOOKUP = {
    "range" : WinnowVersion,
    "design" : WinnowVersion,
    "process" : WinnowProcess,
    "material" : WinnowMaterial,
    "finish" : WinnowFinish,
    "product" : WinnowProduct,
    "fileset" : WinnowFileset,
    "context" : WinnowVersion,
    "choice" : WinnowVersion,
    "contextualised_product" : WinnowVersion,
    "quantified_configuration" : WinnowQuantifiedConfiguration,
}


def publish(db, as_json):
    cls = FACTORY_LOOKUP[as_json[u"type"]]
    return cls.publish(db, as_json)


def get_customer_contexts(session_id):

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
    expanded = product.expanded()

    qc_doc = deepcopy(expanded.get_doc())
    product_doc = product.get_doc()

    version = product_doc["version"]

    qc_doc[u"type"] = "quantified_configuration"
    qc_doc[u"schema"] = "https://opendesk.cc/schemata/options.json"
    qc_doc[u"product"] = "%s@%s.%s.%s" % (product_doc["path"], version[0], version[1], version[2])

    return WinnowQuantifiedConfiguration.merged(db, qc_doc, {}, expanded, choice_document)


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


    return quantified_configuration.get_filesets(db)






