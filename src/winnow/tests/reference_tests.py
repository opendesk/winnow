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

        # self.assertEqual(processes[u"values"], [u'$ref:/processes/fine-sanding', u'$ref:/processes/oiling'])

        inlined = self.premium_birch_ply.inlined()
        inlined_sanding_value =  inlined.get_doc()[u"options"][u"processes"][u"values"][0]
        self.assertEqual(inlined_sanding_value, self.fine_sanding_process.get_doc())


    def test_refs_recurse(self):


        processes = self.premium_birch_ply.get_doc()[u"options"][u"processes"]
        self.assertEqual(processes[u"type"], u'set::resource')

        self.assertEqual(processes[u"values"], [u'$ref:/processes/fine-sanding', u'$ref:/processes/oiling'])
        inlined = self.premium_birch_ply.inlined()
        inlined_sanding_value =  inlined.get_doc()[u"options"][u"processes"][u"values"][0]


        self.assertEqual(inlined_sanding_value, self.fine_sanding_process.get_doc())
        inlined_material_options =  inlined.get_doc()[u"options"][u"material"][u"values"][u"options"]
        self.assertTrue(u"size" in inlined_material_options.keys())
        size = inlined_material_options[u"size"]
        self.assertEqual(size[u"description"], u'available sheet sizes')


    def test_internal_refs(self):
        product = self.add_doc_at_data_path("product_with_internal_refs.json")
        inlined = product.inlined()
        doc = inlined.get_doc()
        self.assertEqual(doc[u"definitions"][u"colour"], doc[u"options"][u"material"][u"values"][0]["options"]["colour"])


    def test_inline_and_scope(self):
        product = self.add_doc_at_data_path("product_with_finishes.json")
        inlined = product.inlined()
        scoped = inlined.scoped("client")
        doc = scoped.get_doc()
        self.assertEqual(len(doc["options"]["finish"]["values"]), 3)
        self.assertEqual(doc["options"]["finish"]["values"][0]["options"], {})

    def test_quantified(self):
        product = self.add_doc_at_data_path("product_with_finishes.json")
        inlined = product.inlined()
        scoped = inlined.scoped("client")
        quantified = scoped.quantified()
        print quantified




    # def expanded_path_matches_ref(self):
    #
    #     product = self.add_doc_at_data_path("product_with_finishes.json")
    #     fine_sanding_process = self.add_doc_at_data_path("processes/fine-sanding/process.json")
    #     light_sanding_process = self.add_doc_at_data_path("processes/light-sanding/process.json")
    #     oiling_process = self.add_doc_at_data_path("processes/oiling/process.json")
    #     birch_ply_material = self.add_doc_at_data_path("birch-ply/material.json")
    #     wisa_material = self.add_doc_at_data_path("wisa-multiwall/material.json")
    #     premium_birch_ply = self.add_doc_at_data_path("finishes/premium-birch-ply/finish.json")
    #     standard_birch_ply = self.add_doc_at_data_path("finishes/standard-birch-ply/finish.json")
    #     premium_wisa = self.add_doc_at_data_path("finishes/premium-wisa/finish.json")
    #     plywood = self.add_doc_at_data_path("plywood/material.json")
    #
    #     inlined = product.inlined()
    #
    #     scoped = inlined.scoped("client")
    #
    #     choice = {
    #         u"schema": u"https://opendesk.cc/schemata/options.json",
    #         u"type": u"choice",
    #         "options":{
    #             "finish": "/finishes/opendesk/premium-birch-ply",
    #             "quantity": 3
    #         }
    #     }





    # def test_merge_refs(self):
    #
    #     product = self.add_doc_at_data_path("product_with_refs.json")
    #     context = self.add_doc_at_data_path("material_context.json")
    #
    #     merged = WinnowProduct.merged(self.db, product.get_doc(), {}, product, context)
    #
    #
    # def test_upstream_refs(self):
    #
    #     fine_sanding_process = self.add_doc_at_data_path("processes/fine-sanding/process.json")
    #     oiling_process = self.add_doc_at_data_path("processes/oiling/process.json")
    #     birch_ply_material = self.add_doc_at_data_path("birch-ply/material.json")
    #     wisa_material = self.add_doc_at_data_path("wisa-multiwall/material.json")
    #     standard_birch_ply = self.add_doc_at_data_path("finishes/standard-birch-ply/finish.json")
    #     premium_birch_ply = self.add_doc_at_data_path("finishes/premium-birch-ply/finish.json")
    #     premium_wisa = self.add_doc_at_data_path("finishes/premium-wisa/finish.json")
    #     product = self.add_doc_at_data_path("product_with_finishes.json")
    #
    #     inlined = product.inlined()
    #     #
    #     print inlined











