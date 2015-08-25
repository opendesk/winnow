import os
import json
import unittest
import winnow
from winnow.models.base import WinnowVersion
from winnow.operations import OptionsExceptionReferenceError
from db import MockKVStore


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestValidateReferences(unittest.TestCase):


    def test_validate_refs(self):

        with open(os.path.join(DATA_DIR, "product_with_components.json"), "r") as f:
            product_dict = json.loads(f.read())

        winnow.validate(product_dict)


class TestExpandReferences(unittest.TestCase):

    def add_doc_at_data_path(self, path):

        with open(os.path.join(DATA_DIR, path), "r") as f:
            as_dict = json.loads(f.read())

        return WinnowVersion.add_doc(self.db, as_dict, {})


    def setUp(self):
        self.db = MockKVStore()

        self.fine_sanding_process = self.add_doc_at_data_path("processes/fine-sanding/process.json")
        self.light_sanding_process = self.add_doc_at_data_path("processes/light-sanding/process.json")
        self.oiling_process = self.add_doc_at_data_path("processes/oiling/process.json")
        self.birch_ply_material = self.add_doc_at_data_path("birch-ply/material.json")
        self.wisa_material = self.add_doc_at_data_path("wisa-multiwall/material.json")
        self.premium_birch_ply = self.add_doc_at_data_path("finishes/premium-birch-ply/finish.json")
        self.standard_birch_ply = self.add_doc_at_data_path("finishes/standard-birch-ply/finish.json")
        self.premium_wisa = self.add_doc_at_data_path("finishes/premium-wisa/finish.json")
        self.plywood = self.add_doc_at_data_path("plywood/material.json")


    def test_expand_refs_from_string(self):

        processes = self.premium_birch_ply.get_doc()[u"options"][u"processes"]
        self.assertEqual(processes[u"type"], u'set::resource')
        expanded = self.premium_birch_ply.expanded()
        expanded_sanding_value =  expanded.get_doc()[u"options"][u"processes"][u"values"][0]
        self.assertEqual(expanded_sanding_value, self.fine_sanding_process.get_doc())


    def test_refs_recurse(self):

        processes = self.premium_birch_ply.get_doc()[u"options"][u"processes"]
        self.assertEqual(processes[u"type"], u'set::resource')
        self.assertEqual(processes[u"values"], [u'$ref:/processes/fine-sanding', u'$ref:/processes/oiling'])
        expanded = self.premium_birch_ply.expanded()
        expanded_sanding_value =  expanded.get_doc()[u"options"][u"processes"][u"values"][0]
        self.assertEqual(expanded_sanding_value, self.fine_sanding_process.get_doc())
        expanded_material_options =  expanded.get_doc()[u"options"][u"material"][u"values"][u"options"]
        self.assertTrue(u"size" in expanded_material_options.keys())
        size = expanded_material_options[u"size"]
        self.assertEqual(size[u"description"], u'available sheet sizes')


    def test_internal_refs(self):
        product = self.add_doc_at_data_path("product_with_internal_refs.json")
        expanded = product.expanded()
        doc = expanded.get_doc()
        self.assertEqual(doc[u"definitions"][u"colour"], doc[u"options"][u"material"][u"values"][0]["options"]["colour"])

    def test_inline_and_scope(self):
        product = self.add_doc_at_data_path("product_with_finishes.json")
        expanded = product.expanded()
        scoped = expanded.scoped(["client"])
        doc = scoped.get_doc()
        self.assertEqual(len(doc["options"]["finish"]["values"]), 3)
        self.assertEqual(doc["options"]["finish"]["values"][0]["options"], {})

    def test_inline_and_multiple_scope(self):
        product = self.add_doc_at_data_path("product_with_finishes.json")
        expanded = product.expanded()
        scoped = expanded.scoped(["client", "maker"])
        doc = scoped.get_doc()
        self.assertEqual(len(doc["options"]["finish"]["values"]), 3)
        self.assertNotEquals(doc["options"]["finish"]["values"][0]["options"], {})

    def test_quantified(self):
        product = self.add_doc_at_data_path("product_with_finishes.json")
        expanded = product.expanded()
        scoped = expanded.scoped(["client"])
        quantified = scoped.quantified()
        doc = quantified.get_doc()
        self.assertEqual(doc["options"]["finish"]["values"][0]["options"], {})

    def test_expand_from_object_ref(self):
        material = self.add_doc_at_data_path("ref_tests/wisa-multiwall/material.json")
        product = self.add_doc_at_data_path("fileset_with_ref.json")
        expanded = product.expanded()
        doc = expanded.get_doc()
        self.assertEqual(doc["options"]["*/material"]["name"], "WISA Multiwall")

    def test_inline_and_scope_in_values(self):
        product = self.add_doc_at_data_path("product_with_finishes.json")
        expanded = product.expanded()
        scoped = expanded.scoped(["client"])
        doc = scoped.get_doc()
        self.assertEqual(len(doc["options"]["size"]["values"]), 1)


        # self.birch_ply_material



    """
    a merge should automatically expand and then unexpand
    expanded things that remain unchanged after merge should be unexpanded again

    """





