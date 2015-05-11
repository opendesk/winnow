import winnow
from winnow.models.base import WinnowVersion
from winnow.models.product import WinnowProduct
from winnow.exceptions import OptionsExceptionFailedValidation, OptionsExceptionReferenceError, OptionsExceptionNoAllowed



class WinnowFileset(WinnowVersion):

    @classmethod
    def publish(cls, db, fileset_json):

        winnow.validate(fileset_json)
        path_elements = fileset_json["path"].split("/")

        if len(path_elements) != 6:
            raise OptionsExceptionFailedValidation("Fileset path should have 5 elements %s" % path_elements)

        product_path = "/".join(path_elements[:-1])
        product = WinnowProduct.get_from_path(db, product_path)

        if product is None:
            raise OptionsExceptionReferenceError("Reference Error: couldn't find %s" % product_path)

        expanded_version = product.expanded()
        kwargs = {"product_version_hash": expanded_version.get_doc_hash()}

        fileset = WinnowFileset.add_doc(db, fileset_json, kwargs=kwargs)

        if not product.allows(fileset):
            raise OptionsExceptionNoAllowed

        db.index_fileset(product_path, fileset.kwargs[u"uuid"])

        return fileset

