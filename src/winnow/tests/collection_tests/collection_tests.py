import os
import json
import unittest
import winnow
from winnow.models.base import WinnowVersion
from winnow.operations import OptionsExceptionReferenceError
from winnow.tests.db import MockKVStore


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

COLLECTION_PATH = "/Users/paul/Dropbox/paulharter/OpenDesk/collection"

class TestExpandReferences(unittest.TestCase):

    def add_doc_at_data_path(self, path):
        print "adding %s" % path

        with open(os.path.join(DATA_DIR, path), "r") as f:
            as_dict = json.loads(f.read())

        return WinnowVersion.add_doc(self.db, as_dict, {})

    def add_all_files_below(self, collection_directory):

        def add_files(arg, dir_name, names):
            for file_name in names:
                file_path = os.path.join(dir_name, file_name)
                if os.path.isfile(file_path):
                    if file_name.endswith(".json"):
                        self.add_doc_at_data_path(file_path)

        os.path.walk(collection_directory, add_files, None)


    def setUp(self):
        self.db = MockKVStore()
        self.add_all_files_below(COLLECTION_PATH)


    def test_materials_context(self):
        materials_context = self.add_doc_at_data_path(os.path.join(COLLECTION_PATH, "contexts/opendesk/standard-materials/context.json"))
        lean_desk = self.add_doc_at_data_path(os.path.join(DATA_DIR, "leandesk/product.json"))
        expanded = lean_desk.expanded()