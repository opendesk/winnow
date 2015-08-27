import os
import json
import unittest
import winnow
from winnow.models.base import WinnowVersion
from winnow.operations import OptionsExceptionReferenceError
from winnow.tests.db import MockKVStore
from winnow.pipeline import flow
from winnow.utils import json_dumps


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

COLLECTION_PATH = "/Users/paul/Dropbox/paulharter/OpenDesk/opendesk-collection"

class TestExpandReferences(unittest.TestCase):

    def add_doc_at_data_path(self, path):

        with open(os.path.join(DATA_DIR, path), "r") as f:
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
        self.all_files = self.add_all_files_below(COLLECTION_PATH)

    def test_expand_all(self):
        for f in self.all_files:
            expanded = f.expanded()


    def test_get_default_product_options(self):

        session_id = u"12345"
        product_path = u"/ranges/lean/desk/long-wide"
        default_product_options = flow.get_default_product_options(self.db, product_path, session_id)
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


    def test_make_a_manufacturing_spec(self):

        session_id = u"12345"
        product_path = u"/ranges/lean/desk/mid-long-wide"
        default_product_options = flow.get_default_product_options(self.db, product_path, session_id)
        choices = {
            u"configuration": u"strange-tops",
            u"material-choices": {
                u"type": u"set::string",
                u"values": {
                    u"type": u"string",
                    u"value": u"birch-ply",
                    u"options":{
                        u"finish": u"$ref:/finishes/opendesk/premium-birch-ply"
                    }
                }
            },
            u"quantity": 1
        }

        quantified_configuration = flow.get_quantified_configuration(self.db, product_path, choices)
        filesets = flow.get_filesets_for_quantified_configuration(self.db, quantified_configuration)
        fileset = filesets[0]["fileset"]

        # print fileset
        # print quantified_configuration

        manufacturing_spec = flow.get_manufacturing_spec(self.db, quantified_configuration, fileset)

        #
        print manufacturing_spec



        # files = fileset.get_doc()["files"]
        # found_files = [f["asset"].split("/")[-1] for f in files]
        # expected_files = [
        #     "LEN_DSK_LGW_C-PT_A-SA_M-AP_cad-1_18.00~0.0.dxf",
        #     "LEN_DSK_LGW_C-PT_A-SA_M-AP_cad-2_18.00~0.0.dxf",
        #     "LEN_DSK_LGW_C-PT_A-SA_M-AP_cad-3_18.00~0.0.dxf",
        #     "LEN_DSK_LGW_C-PT_A-SA_M-AP_cad-4_18.00~0.0.dxf"
        # ]
        #
        # self.assertEqual(found_files, expected_files)