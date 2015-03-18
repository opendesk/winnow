import os
import unittest
import json
import time
from decimal import Decimal
from db import MockKVStore
import winnow.utils as utils
from winnow.exceptions import OptionsExceptionReferenceError
import winnow.pipeline.flow as flow

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


DEFAULT_QUANTITY = {
    "schema": "https://opendesk.cc/schemata/options.json",
    "type": "context",
    "name": "Default Quantity",
    "options":{
        "quantity": {
            "type": "numeric::step",
            "name": "Quantity",
            "max": 10000,
            "min": 1,
            "start": 1,
            "step": 1
        }
    }
}


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
        as_dict = dict_at_data_path(path)
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


    def test_publish_product_fail_upstream(self):
        as_dict = dict_at_data_path("product_with_thickness.json")
        self.assertRaises(OptionsExceptionReferenceError, flow.publish, self.db, as_dict)


    def test_publish_product(self):
        as_dict = dict_at_data_path("product_with_thickness_parent.json")
        flow.publish(self.db, as_dict)

        as_dict = dict_at_data_path("product_with_thickness.json")
        product = flow.publish(self.db, as_dict)


    def test_publish_product_expanded(self):

        as_dict = dict_at_data_path("product_with_thickness_parent.json")
        flow.publish(self.db, as_dict)

        as_dict = dict_at_data_path("product_with_thickness.json")
        product = flow.publish(self.db, as_dict)

        expanded = product.expanded()

        print expanded

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

class TestMakeQuantifiedConfiguration(unittest.TestCase):


    def setUp(self):
        self.maxDiff = None
        self.db = MockKVStore()

    def _publish(self, path):

        as_dict = dict_at_data_path(path)
        return flow.publish(self.db, as_dict)


    def test_make_quantified_configuration(self):

        as_dict = dict_at_data_path("product_with_thickness_parent.json")
        flow.publish(self.db, as_dict)

        context = self._publish("uk_context.json")
        quantity = self._publish("default_quantity.json")
        as_dict = dict_at_data_path("product_with_thickness.json")
        product = flow.publish(self.db, as_dict)
        quantified_configuration = flow.get_default_quantified_configuration(self.db, product, ["/contexts/uk/production", "/contexts/default_quantity"])

        print quantified_configuration


    def test_update_quantified_configuration(self):

        as_dict = dict_at_data_path("product_with_thickness_parent.json")
        flow.publish(self.db, as_dict)

        context = self._publish("uk_context.json")
        quantity = self._publish("default_quantity.json")

        as_dict = dict_at_data_path("product_with_thickness.json")
        product = flow.publish(self.db, as_dict)
        quantified_configuration = flow.get_default_quantified_configuration(self.db, product, ["/contexts/uk/production", "/contexts/default_quantity"])

        choice = self._publish("choice.json")
        updated_quantified_configuration = flow.get_updated_quantified_configuration(self.db, quantified_configuration, choice)



    def test_get_filesets(self):

        as_dict = dict_at_data_path("product_with_thickness_parent.json")
        flow.publish(self.db, as_dict)

        self._publish("uk_context.json")
        self._publish("default_quantity.json")

        as_dict = dict_at_data_path("product_with_thickness.json")
        product = flow.publish(self.db, as_dict)

        self._publish("fileset.json")
        self._publish("fileset2.json")
        self._publish("fileset3.json")

        quantified_configuration = flow.get_default_quantified_configuration(self.db, product, ["/contexts/uk/production", "/contexts/default_quantity"])

        choice = self._publish("choice.json")
        updated_quantified_configuration = flow.get_updated_quantified_configuration(self.db, quantified_configuration, choice)

        filesets = flow.get_filesets_for_quantified_configuration(self.db, updated_quantified_configuration)

        self.assertTrue(len(filesets) == 2)
        self.assertTrue(filesets[0][u"matched"] == set([u'material', u'sheet']))
        self.assertTrue(filesets[1][u"matched"] == set([u'sheet']))
        self.assertEqual(filesets[0][u"fileset"].kwargs[u"doc"][u"files"], [{u'asset': u'files/test_3.txt'}, {u'asset': u'files/test_4.txt'}])
        self.assertEqual(filesets[1][u"fileset"].kwargs[u"doc"][u"files"], [{u'asset': u'files/test_5.txt'}, {u'asset': u'files/test_6.txt'}])




























