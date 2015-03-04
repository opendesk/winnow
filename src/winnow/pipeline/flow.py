from copy import deepcopy
import winnow

from winnow.models.product import WinnowProduct
from winnow.models.fileset import WinnowFileset
from winnow.models.process import WinnowProcess
from winnow.models.material import WinnowMaterial
from winnow.models.finish import WinnowFinish
from winnow.models.base import WinnowVersion
from winnow.models.quantified_configuration import WinnowQuantifiedConfiguration

"""
1. product model published
  - validate (the product documents)
  - patch (to expand the child document with the parent graph)
  -> inputs: product documents, upstream product graph
  => outputs: product documents
"""

FACTORY_LOOKUP = {
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


def get_default_quantified_configuration(db, product, context_paths):
    return product.get_default_quantified_configuration(db, context_paths)


def get_updated_quantified_configuration(db, quantified_configuration, choice_document):
    return quantified_configuration.get_updated(db, choice_document)


def get_filesets_for_quantified_configuration(db, quantified_configuration):
    return quantified_configuration.get_filesets(db)






