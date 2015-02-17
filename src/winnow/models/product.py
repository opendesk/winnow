import winnow
from winnow.models.base import WinnowVersion
from winnow.exceptions import OptionsExceptionFailedValidation


class WinnowProduct(WinnowVersion):

    @classmethod
    def publish(cls, db, product_json):
        product = cls.add_doc(db, product_json)
        expanded = product.expanded()
        expanded.validate()
        return product


