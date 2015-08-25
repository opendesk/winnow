import os
import decimal
import json

import unittest
from winnow.models.base import WinnowVersion
from winnow.values.option_values import OptionResourceWinnowValue
from winnow.options import OptionsSet
from winnow.inline import _merge_option_dicts
from winnow.utils import json_dumps
from winnow.values import value_factory, value_path_factory
from db import MockKVStore


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestOptionResourceWinnowValue(unittest.TestCase):

    def test_prune_children(self):
        paths = ["a/b/c", "a/b", "a/b/d", "f/g"]
        pruned = OptionResourceWinnowValue._prune_child_nodes(paths)
        self.assertEqual(pruned,  ["a/b", "f/g" ])

    def test_relatedness(self):

        are_related = OptionResourceWinnowValue._are_related_in_taxonomy
        self.assertTrue(are_related("a/b", "a/b/c"))
        self.assertTrue(are_related("a/b", "a/b/d"))
        self.assertFalse(are_related("a/b/c", "a/b/d"))
        self.assertTrue(are_related("a/b/c", "a/b"))

    def test_intersection(self):

        intersection = OptionResourceWinnowValue._intersection_of_path_sets
        self.assertEqual(intersection(["a/b"], ["a/b/c"]), ["a/b/c"])
        self.assertEqual(intersection(["a/b", "f/g"], ["a/b/c"]), ["a/b/c"])

    def test_nearest_match(self):

        nearest = OptionResourceWinnowValue._nearest_match
        self.assertEqual(nearest("a/b", ["a", "a/b/c"]), "a")
        self.assertEqual(nearest("a/b", ["a", "a/b", "a/b/c"]), "a/b")
        self.assertEqual(nearest("a/b/c", ["a", "a/b"]), "a/b")
        self.assertEqual(nearest("a", ["a/b/c", "a/b"]), None)


class TestTaxonomyValuesWithCollection(unittest.TestCase):

    def setUp(self):
        self.db = MockKVStore()



    def test_making_options_collection(self):

        fileset_dict =  {
            "type": "fileset",
            "schema": "https://opendesk.cc/schemata/fileset.json",
            "source": "http://localhost:5100/api/v1/open",
            "path": "/ranges/kerf/kerf-chair/standard-public/miy-download",
            "aliases": [
                "/ranges/kerf/kerf-chair/standard/plywood",
                "/ranges/kerf/kerf-chair/standard/page-20150728-150527"
            ],
            "name": "MIY Download",
            "description": "",
            "category": "sheets",
            "files": {
                "airfix-0": {
                    "name": "Airfix",
                    "slug": "airfix-0",
                    "num_sheets": 1
                }
            },
            "manufacturing": {
                "cutting": {
                    "total_sheets": 1
                },
                "strategies": {
                    "A": {
                        "type": "string",
                        "value": "A",
                        "sheets": [
                            {
                                "sheet": "$ref:~/files/airfix-0",
                                "use": "$ref:/materials"
                            }
                        ]
                    }
                }
            },
            "options": {
                "*/material": [
                    {
                        "$ref": "/materials",
                        "options": {
                            "strategy": {
                                "type": "set::string",
                                "default": "$ref:~/manufacturing/strategies/A",
                                "scopes": [
                                    "maker",
                                    "operator"
                                ],
                                "values": [
                                    "$ref:~/manufacturing/strategies/A"
                                ]
                            }
                        }
                    }
                ]
            },
            "changes": "Initial version",
            "version": [
                1,
                0,
                0
            ]
        }


class TestTaxonomyValues(unittest.TestCase):


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



    def test_making_options(self):

        options_dict_a =  {
            u"*/finish": [
                {
                    u"$ref": u"/finishes/opendesk/premium-birch-ply"
                },
                {
                    u"$ref": u"/finishes/opendesk/premium-wisa",
                    u"options": {
                        u"strategies": {
                            u"default": "",
                            u"scopes": [
                                u"maker",
                                u"operator"
                            ],
                            u"type": u"set::string",
                            u"values": [
                                u"poo",
                                u"bum"
                            ]
                        }
                    }
                }
            ]
        }

        options_dict_b =  {
            u"configuration": u"straight-tops",
            u"material-choices": {
                u"default": u"wisa",
                u"name": u"Material",
                u"type": u"set::string",
                u"values": {
                    u"name": u"Wisa",
                    u"options": {
                        u"finish": u"$ref:/finishes/opendesk/premium-wisa"
                    },
                    u"type": u"string",
                    u"value": u"wisa"
                }
            }
        }

        source = self.premium_birch_ply

        merged = _merge_option_dicts(source, options_dict_a, options_dict_b)

        self.assertEquals(merged.keys(), [u'configuration', u'material-choices'])


        material_choice = merged[u'material-choices'][u"values"]

        print material_choice

        self.assertEquals(material_choice[u"value"], u"wisa")

        self.assertEquals(material_choice[u"options"][u"finish"][u"options"].keys(), [u'strategies', u'processes', u'material'])


class TestTaxonomy(unittest.TestCase):


    def setUp(self):
        self.db = MockKVStore()

        snot = {
            u"type": u"stuff",
            u"path": u"/stuff/bodilyfluids/snot",
            u"options":{
                u"colours": [u"green", u"yellow"],
            }
        }

        bodilyfluids = {
            u"type": u"stuff",
            u"path": u"/stuff/bodilyfluids",
            u"options":{}
        }

        drink = {
            u"type": u"drink",
            u"path": u"/drinks/cocktail",
            u"options":{
                u"stuff": u"$ref:/stuff/bodilyfluids"
            }
        }


        WinnowVersion.add_doc(self.db, snot, {})
        WinnowVersion.add_doc(self.db, bodilyfluids, {})
        self.drink = WinnowVersion.add_doc(self.db, drink, {})



    def test_match_taxonomy(self):

        mixer_doc = {
            u"type": u"mixers",
            u"path": u"/mixers/best",
            u"options":{
                u"stuff": u"$ref:/stuff/bodilyfluids/snot"

            }
        }

        mixer_doc_2 = {
            u"type": u"mixers",
            u"path": u"/mixers/best",
            u"options":{
                u"stuff": u"$ref:/stuff/bodilyfluids"
            }
        }

        mixer = WinnowVersion.add_doc(self.db, mixer_doc, {})
        mixer_2 = WinnowVersion.add_doc(self.db, mixer_doc_2, {})

        # try merging identical references with each other
        merged = WinnowVersion.merged(self.db, self.drink.get_doc(), {}, self.drink, mixer_2)

        self.assertEqual(merged.get_doc(), self.drink.get_doc())

        # try merging child/parent
        merged = WinnowVersion.merged(self.db, mixer_doc, {}, self.drink, mixer)
        #
        self.assertEqual(merged.get_doc(), mixer_doc)