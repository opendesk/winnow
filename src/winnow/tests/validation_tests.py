import unittest

import winnow
from winnow.exceptions import OptionsExceptionFailedValidation



class TestReferenceValidation(unittest.TestCase):



    def test_regex(self):

        # empty
        doc = {
            u"schema": u"https://opendesk.cc/schemata/options.json",
            u"type": u"option",
            u"options":{
            }
        }

        winnow.validate(doc)

        # with a string ref
        doc = {
            u"schema": u"https://opendesk.cc/schemata/options.json",
            u"type": u"option",
            u"options":{
                u"inline": u"$ref:/something/that/should/pass"
            }
        }

        winnow.validate(doc)

        # with an object ref
        doc = {
            u"schema": u"https://opendesk.cc/schemata/options.json",
            u"type": u"option",
            u"options":{
                u"inline": {
                    u"$ref": u"/something/that/should/pass"
                }
            }
        }

        winnow.validate(doc)

        # with an object ref with options
        doc = {
            u"schema": u"https://opendesk.cc/schemata/options.json",
            u"type": u"option",
            u"options":{
                u"inline": {
                    u"$ref": u"/something/that/should/pass",
                    u"options":{}
                }
            }
        }

        winnow.validate(doc)

        # extra attrs should fail
        doc = {
            u"schema": u"https://opendesk.cc/schemata/options.json",
            u"type": u"option",
            u"options":{
                u"inline": {
                    u"$ref": u"/something/that/should/pass",
                    u"options":{},
                    u"should_fail": {}
                }
            }
        }

        self.assertRaises(OptionsExceptionFailedValidation, winnow.validate, doc )



        # any string should pass
        doc = {
            u"schema": u"https://opendesk.cc/schemata/options.json",
            u"type": u"option",
            u"options":{
                u"inline": u"something/that/should/pass"
            }
        }

        winnow.validate(doc)

        # except if it starts with a $ but isnt a correct ref
        doc = {
            u"schema": u"https://opendesk.cc/schemata/options.json",
            u"type": u"option",
            u"options":{
                u"inline": u"$ref/something/that/should/fail"
            }
        }

        self.assertRaises(OptionsExceptionFailedValidation, winnow.validate, doc )