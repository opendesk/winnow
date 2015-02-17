import os
import unittest
import json
import time
from decimal import Decimal
from db import MockKVStore
import winnow.utils as utils
import winnow.pipeline.flow as flow

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def get_timestamp():
    return unicode(time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()))


def dict_at_data_path(path):
    with open(os.path.join(DATA_DIR, path), "r") as f:
        return utils.json_loads(f.read())


class TestPublishingResources(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.db = MockKVStore()


    def _publish(self, path):

        as_dict = dict_at_data_path("processes/fine-sanding/process.json")
        flow.publish(self.db, as_dict)


    def test_publish_product_sieve(self):

        fine_sanding_process = self._publish("processes/fine-sanding/process.json")
        oiling_process = self._publish("processes/oiling/process.json")
        birch_ply_material = self._publish("birch-ply/material.json")
        wisa_material = self._publish("wisa-multiwall/material.json")
        premium_birch_ply = self._publish("finishes/premium-birch-ply/finish.json")
        premium_wisa = self._publish("finishes/premium-wisa/finish.json")


class TestPublishingProduct(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.db = MockKVStore()


    def test_publish_product(self):

        as_dict = dict_at_data_path("product_with_components.json")
        product = flow.publish(self.db, as_dict)
        expanded = product.expanded()



class TestPublishingFileset(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.db = MockKVStore()


    def test_publish_fileset(self):
        as_dict = dict_at_data_path("product_with_components.json")
        product = flow.publish(self.db, as_dict)
        as_dict = dict_at_data_path("fileset.json")
        fileset = flow.publish(self.db, as_dict)
        self.assertEqual(fileset.kwargs["product_version_hash"], product.kwargs["doc_hash"])

