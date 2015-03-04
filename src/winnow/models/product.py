import winnow
from winnow.models.base import WinnowVersion

from winnow.models.quantified_configuration import WinnowQuantifiedConfiguration
from winnow.exceptions import OptionsExceptionFailedValidation


class WinnowProduct(WinnowVersion):

    @classmethod
    def publish(cls, db, product_json):
        product = cls.add_doc(db, product_json)
        expanded = product.expanded()
        expanded.validate()
        return product


    def get_default_quantified_configuration(self, db, context_paths):

        expanded = self.expanded()

        doc = {}
        doc[u"type"] = "quantified_configuration"
        doc[u"schema"] = "https://opendesk.cc/schemata/options.json"

        # scoped = expanded.scoped(db, doc, ["client"])
        #
        for context_path in context_paths:
            context = WinnowVersion.get_from_path(db, context_path)
            merged = WinnowQuantifiedConfiguration(db, {})
            winnow.merge(expanded, context, merged, doc)
            expanded = merged

        scoped = expanded.scoped(db, doc, ["client"])

        db.set(scoped.kwargs[u"uuid"], scoped.kwargs)
        return scoped


    def get_filesets(self, db):
        from winnow.models.fileset import WinnowFileset
        fileset_ids = db.fileset_ids_for_product_path(self.kwargs["doc"]["path"])
        return [WinnowFileset.get_from_id(db, fileset_id) for fileset_id in  fileset_ids]





