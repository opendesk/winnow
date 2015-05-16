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


    def get_filesets(self, db):
        from winnow.models.fileset import WinnowFileset
        fileset_ids = db.fileset_ids_for_product_path(self.kwargs["doc"]["path"])
        return [WinnowFileset.get_from_id(db, fileset_id) for fileset_id in  fileset_ids]





