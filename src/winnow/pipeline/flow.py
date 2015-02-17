from winnow.models.product import WinnowProduct
from winnow.models.fileset import WinnowFileset
from winnow.models.process import WinnowProcess
from winnow.models.material import WinnowMaterial
from winnow.models.finish import WinnowFinish

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
    "fileset" : WinnowFileset
}


def publish(db, as_json):
    cls = FACTORY_LOOKUP[as_json[u"type"]]
    return cls.publish(db, as_json)


