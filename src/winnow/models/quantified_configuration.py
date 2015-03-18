import winnow
from winnow.models.base import WinnowVersion



class WinnowQuantifiedConfiguration(WinnowVersion):

    def get_updated(self, db, choice_document):
        doc = {}
        doc[u"type"] = "quantified_configuration"
        doc[u"schema"] = "https://opendesk.cc/schemata/options.json"
        return WinnowQuantifiedConfiguration.merged(db, doc, {}, self, choice_document)

    def get_product(self, db):
        from winnow.models.product import WinnowProduct
        history = self.kwargs["history"]
        first = history[0]
        if first.get("action") != u"START":
            raise Exception("the history shoud have a start")
        return WinnowProduct.get_from_id(db, first["input_id"])

    def get_filesets(self, db):

        product = self.get_product(db)
        filesets = product.get_filesets(db)
        matching = winnow.filter_allowed_by(self, filesets)

        self_keys = set(self.get_doc()[u"options"].keys())

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