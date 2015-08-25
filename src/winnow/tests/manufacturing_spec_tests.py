import os

import unittest
from winnow.models.base import WinnowVersion
from winnow.values.option_values import OptionResourceWinnowValue
from db import MockKVStore

from winnow.utils import json_loads


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestCreateManufacturingSpec(unittest.TestCase):

    def add_doc_at_data_path(self, path):

        with open(os.path.join(DATA_DIR, path), "r") as f:
            as_dict = json_loads(f.read())

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

        self.fileset = self.add_doc_at_data_path("fileset_with_components.json")

        self.product = self.add_doc_at_data_path("product_with_finishes.json")


    def test_make_manufacturing_spec(self):

        expanded = self.fileset.expanded({})

        expanded = self.product.expanded()
        scoped = expanded.scoped(["client"])
        quantified = scoped.quantified()
        doc = quantified.get_doc()




