import os
from copy import deepcopy
import unittest
import winnow
from winnow.models.base import WinnowVersion

from db import MockKVStore


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestUnexpandReferences(unittest.TestCase):


    def setUp(self):
        self.db = MockKVStore()

        self.dog_base_choices = {
            "type": "choices",
            "path": "/choices/dog_choices",
            "options":{
                "colours": ["brown", "white", "red"],
            }
        }

        breed1 = {
            "type": "dog",
            "path": "/breeds/collie",
            "options":{
                "colours": "$ref:/choices/dog_choices~/options/colours",
                "size": ["big", "small"]
            }
        }

        breed2 = {
            "type": "dog",
            "path": "/breeds/sausage",
            "options":{
                "colours": "$ref:/choices/dog_choices~/options/colours"
            }
        }


        WinnowVersion.add_doc(self.db, self.dog_base_choices, {})
        WinnowVersion.add_doc(self.db, breed1, {})
        WinnowVersion.add_doc(self.db, breed2, {})


    """
    a merge should automatically expand and then unexpand
    expanded things that remain unchanged after merge should be unexpanded again

    """

    def test_expand_key_hash_creation(self):

        breed1 = WinnowVersion.get_from_path(self.db, "/breeds/collie")

        ref_hashes = {}
        expanded_doc = deepcopy(breed1.get_doc())
        winnow.inline.inline_refs(expanded_doc, breed1, ref_hashes)
        value = u"$ref:/choices/dog_choices~/options/colours"
        colour_options = self.dog_base_choices["options"]["colours"]
        hash = winnow.utils.get_doc_hash(winnow.utils.json_dumps(colour_options))
        self.assertEqual(ref_hashes.get(hash), value)
        self.assertEqual(expanded_doc["options"]["colours"], ["brown", "white", "red"])


    def test_unexpand(self):

        breed1 = WinnowVersion.get_from_path(self.db, "/breeds/collie")

        ref_hashes = {}
        expanded_doc = deepcopy(breed1.get_doc())

        winnow.inline.inline_refs(expanded_doc, breed1, ref_hashes)

        ref_value = u"$ref:/choices/dog_choices~/options/colours"
        colour_options = self.dog_base_choices["options"]["colours"]
        hash = winnow.utils.get_doc_hash(winnow.utils.json_dumps(colour_options))
        self.assertEqual(ref_hashes.get(hash), ref_value)
        self.assertEqual(expanded_doc["options"]["colours"], ["brown", "white", "red"])
        winnow.inline.restore_unchanged_refs(expanded_doc, ref_hashes)
        self.assertEqual(expanded_doc["options"]["colours"], ref_value)



    def test_expand_key_hash_creation_2(self):

        breed1 = WinnowVersion.get_from_path(self.db, "/breeds/collie")

        kwargs={}
        expanded = breed1.__class__(breed1.db, kwargs)
        ref_hashes = winnow.expand(breed1, expanded)
        breed1.db.set(expanded.kwargs[u"uuid"], expanded.kwargs)
        value = u"$ref:/choices/dog_choices~/options/colours"
        colour_options = self.dog_base_choices["options"]["colours"]
        hash = winnow.utils.get_doc_hash(winnow.utils.json_dumps(colour_options))

        self.assertEqual(ref_hashes.get(hash), value)


    def test_merge_does_expanding(self):
        
        favorite_colours = {
            "type": "prefs",
            "path": "/prefs/favorites",
            "options":{
                "colours": ["red", "white", "green"]
            }
        }
        
        WinnowVersion.add_doc(self.db, favorite_colours, {})
        breed1 = WinnowVersion.get_from_path(self.db, "/breeds/collie")
        favs = WinnowVersion.get_from_path(self.db, "/prefs/favorites")
        merged = WinnowVersion.merged(self.db, breed1.get_doc(), {}, breed1, favs)
        merged_doc = merged.get_doc()
        self.assertEqual(merged_doc["options"]["colours"], ["red", "white"])



    def test_merge_unexpands_unaffected(self):

        favorite_colours = {
            "type": "prefs",
            "path": "/prefs/favorites",
            "options":{
                "taste": ["bitter", "sour"]
            }
        }

        WinnowVersion.add_doc(self.db, favorite_colours, {})
        breed1 = WinnowVersion.get_from_path(self.db, "/breeds/collie")
        favs = WinnowVersion.get_from_path(self.db, "/prefs/favorites")
        merged = WinnowVersion.merged(self.db, breed1.get_doc(), {}, breed1, favs)
        merged_doc = merged.get_doc()
        self.assertEqual(merged_doc["options"]["colours"], u"$ref:/choices/dog_choices~/options/colours")


    def test_merge_unexpands_unaffected_2(self):

        favorite_colours = {
            "type": "prefs",
            "path": "/prefs/favorites",
            "options":{
                "colours": ["brown", "white", "red"]
            }
        }

        WinnowVersion.add_doc(self.db, favorite_colours, {})
        breed1 = WinnowVersion.get_from_path(self.db, "/breeds/collie")
        favs = WinnowVersion.get_from_path(self.db, "/prefs/favorites")
        merged = WinnowVersion.merged(self.db, breed1.get_doc(), {}, breed1, favs)
        merged_doc = merged.get_doc()
        self.assertEqual(merged_doc["options"]["colours"], u"$ref:/choices/dog_choices~/options/colours")


    def test_merge_unexpands_unaffected_3(self):

        favorite_colours = {
            "type": "prefs",
            "path": "/prefs/favorites",
            "options":{
                "colours": ["brown", "white", "red", "blue"]
            }
        }

        WinnowVersion.add_doc(self.db, favorite_colours, {})
        breed1 = WinnowVersion.get_from_path(self.db, "/breeds/collie")
        favs = WinnowVersion.get_from_path(self.db, "/prefs/favorites")
        merged = WinnowVersion.merged(self.db, breed1.get_doc(), {}, breed1, favs)
        merged_doc = merged.get_doc()
        self.assertEqual(merged_doc["options"]["colours"], u"$ref:/choices/dog_choices~/options/colours")


    def test_merge_unexpands_unaffected_4(self):

        favorite_colours = {
            "type": "prefs",
            "path": "/prefs/favorites",
            "options":{
                "colours": "$ref:/choices/dog_choices~/options/colours",
            }
        }

        WinnowVersion.add_doc(self.db, favorite_colours, {})
        breed1 = WinnowVersion.get_from_path(self.db, "/breeds/collie")
        favs = WinnowVersion.get_from_path(self.db, "/prefs/favorites")
        merged = WinnowVersion.merged(self.db, breed1.get_doc(), {}, breed1, favs)
        merged_doc = merged.get_doc()
        self.assertEqual(merged_doc["options"]["colours"], u"$ref:/choices/dog_choices~/options/colours")