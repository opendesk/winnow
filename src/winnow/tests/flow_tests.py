import os
import json
import unittest
from winnow.tests.db import MockKVStore
from winnow.pipeline import flow

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# this has to be set
COLLECTION_PATH = "/Users/paul/Dropbox/paulharter/OpenDesk/opendesk-collection"


class TestExpandReferences(unittest.TestCase):

    def add_doc_at_data_path(self, path):


        with open(path, "r") as f:
            as_dict = json.loads(f.read())


        doc = flow.publish(self.db, as_dict)

        return doc

    def add_all_files_below(self, collection_directory):

        files = []

        def add_files(arg, dir_name, names):
            for file_name in names:
                file_path = os.path.join(dir_name, file_name)
                if os.path.isfile(file_path):
                    if file_name.endswith(".json"):
                        files.append(self.add_doc_at_data_path(file_path))

        os.path.walk(collection_directory, add_files, None)

        return files


    def setUp(self):
        self.db = MockKVStore()

        if not os.path.exists(COLLECTION_PATH):
            raise Exception("**** DID YOU SET COLLECTION_PATH ***")

        self.all_files = self.add_all_files_below(COLLECTION_PATH)


    def test_get_product_options(self):

        session_id = u"12345"
        product_path = u"/ranges/lean/desk/long-wide"
        product_options = flow.get_default_product_options(self.db, product_path, session_id)


    def test_get_quantified_configuration(self):

        product_path = u"/ranges/lean/desk/long-wide"

        choices = {
            u"configuration": u"profiled-tops",
            u"material-choices": u"birch-ply",
            u"quantity": 1
        }

        quantified_configuration = flow.get_quantified_configuration(self.db, product_path, choices)



    def test_get_filesets(self):

        product_path = u"/ranges/lean/desk/long-wide"

        choices = {
            u"configuration": u"profiled-tops",
            u"material-choices": u"birch-ply",
            u"quantity": 1
        }

        quantified_configuration = flow.get_quantified_configuration(self.db, product_path, choices)
        filesets = flow.get_filesets_for_quantified_configuration(self.db, quantified_configuration)
        fileset = filesets[0]["fileset"]
        files = fileset.get_doc()["files"]

        found_files = [f["asset"].split("/")[-1] for f in files]

        expected_files = [
            "LEN_DSK_LGW_C-PT_A-SA_M-AP_cad-1_18.00~0.0.dxf",
            "LEN_DSK_LGW_C-PT_A-SA_M-AP_cad-2_18.00~0.0.dxf",
            "LEN_DSK_LGW_C-PT_A-SA_M-AP_cad-3_18.00~0.0.dxf",
            "LEN_DSK_LGW_C-PT_A-SA_M-AP_cad-4_18.00~0.0.dxf"
        ]

        self.assertEqual(found_files, expected_files)


    def test_get_other_filesets(self):

        product_path = u"/ranges/lean/desk/mid-long-wide"

        choices = {
            u"configuration": u"straight-tops",
            u"material-choices": {
                u"type": u"set::string",
                u"values": u"standard-laminate"
            },
            u"quantity": 2
        }

        quantified_configuration = flow.get_quantified_configuration(self.db, product_path, choices)
        filesets = flow.get_filesets_for_quantified_configuration(self.db, quantified_configuration)
        fileset = filesets[0]["fileset"]
        files = fileset.get_doc()["files"]

        found_files = [f["asset"].split("/")[-1] for f in files]

        expected_files = [
            "LEN_DSK_MLW_C-ST_A-SA_M-AP_cad-1_18.00~0.0.dxf",
            "LEN_DSK_MLW_C-ST_A-SA_M-AP_cad-2_18.00~0.0.dxf",
            "LEN_DSK_MLW_C-ST_A-SA_M-AP_cad-3_18.00~0.0.dxf",
            "LEN_DSK_MLW_C-ST_A-SA_M-AP_cad-4_18.00~0.0.dxf"
        ]

        self.assertEqual(found_files, expected_files)


    def test_make_manufacturing_spec(self):

        product_path = u"/ranges/lean/desk/mid-long-wide"

        choices = {
            u"configuration": u"straight-tops",
            u"material-choices": {
                u"type": u"set::string",
                u"values": u"standard-laminate"
            },
            u"quantity": 2
        }

        quantified_configuration = flow.get_quantified_configuration(self.db, product_path, choices)
        filesets = flow.get_filesets_for_quantified_configuration(self.db, quantified_configuration)
        fileset = filesets[1]["fileset"]

        manufacturing_spec = flow.get_manufacturing_spec(self.db, quantified_configuration, fileset)

        print manufacturing_spec

        self.assertTrue(manufacturing_spec != None)

        # files = fileset.get_doc()["files"]
        #
        # found_files = [f["asset"].split("/")[-1] for f in files]
        #
        # expected_files = [
        #     "LEN_DSK_MLW_C-ST_A-SA_M-AP_cad-1_18.00~0.0.dxf",
        #     "LEN_DSK_MLW_C-ST_A-SA_M-AP_cad-2_18.00~0.0.dxf",
        #     "LEN_DSK_MLW_C-ST_A-SA_M-AP_cad-3_18.00~0.0.dxf",
        #     "LEN_DSK_MLW_C-ST_A-SA_M-AP_cad-4_18.00~0.0.dxf"
        # ]
        #
        # self.assertEqual(found_files, expected_files)