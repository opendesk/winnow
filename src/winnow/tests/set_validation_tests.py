import unittest

import winnow
from winnow.exceptions import OptionsExceptionFailedValidation



class TestReferenceValidation(unittest.TestCase):



    def test_basic_set(self):

        # empty
        doc = {
            u"schema": u"https://opendesk.cc/schemata/options.json",
            u"type": u"option",
            u"options":{
                u"colour":{
                    u'type': u'set::string',
                    u'values': u'blue'
                }
            }
        }

        winnow.validate(doc)

    def test_list_basic_set(self):

        # empty
        doc = {
            u"schema": u"https://opendesk.cc/schemata/options.json",
            u"type": u"option",
            u"options":{
                u"colour":{
                    u'type': u'set::string',
                    u'values': [u'blue', u'red']
                }
            }
        }

        winnow.validate(doc)

    def test_reference_set(self):

        doc = {
            u"schema": u"https://opendesk.cc/schemata/options.json",
            u"type": u"option",
            u"options":{
                u"processes":{
                    u'scopes': [u'maker'],
                    u'type': u'set::resource',
                    u'values': [
                        u'$ref:/processes/fine-sanding',
                        u'$ref:/processes/oiling'
                    ]
                }
            }
        }

        winnow.validate(doc)


    def test_breaking_set(self):

        doc = {
            u"schema": u"https://opendesk.cc/schemata/options.json",
            u"type": u"option",
            u"options":{
                u"size":{
                    u'description': u'available sheet sizes',
                    u'name': u'sizes',
                    u'type': u'set::string',
                    u'values': [
                        {
                            u'type': u'string',
                            u'value': u'1200x2400'
                        }
                     ]
                }
            }
        }

        winnow.validate(doc)


    def test_breaking_resource(self):

        doc = {
            u"schema": u"https://opendesk.cc/schemata/options.json",
            u"type": u"option",
            u"options":{
                u"size":{
                     u'changes': u'Initial public version.',
                     u'description': u'Pre laminated plywood with polypropylene coating on a lacquered surface.',
                     u'name': u'WISA Multiwall',
                     u'options': {},
                     u'path': u'/materials/opendesk/sheets/wood/composite/plywood/laminated/pre-laminated/wisa-multiwall',
                     u'schema': u'https://opendesk.cc/schemata/material.json',
                     u'source': u'https://github.com/opendesk/collection',
                     u'type': u'material',
                     u'version': [0,0, 1]
                }
            }
        }

        winnow.validate(doc)


    def test_breaking_context(self):

        doc = {
            u"schema": u"https://opendesk.cc/schemata/options.json",
            u"type": u"option",
            u"options":{
                u"size":{
                    u'default': u'birch-ply',
                     u'description': u'Choose a material',
                     u'name': u'Material',
                     u'type': u'set::string',
                     u'values': [{u'description': u'...',
                                  u'images': [{u'asset': u'../assets/publish/lean_logo.png',
                                               u'type': u'banner'}],
                                  u'name': u'Birch Ply',
                                  u'options': {u'finish': {u'default': u'/finishes/opendesk/standard-birch-ply',
                                                           u'scopes': [u'maker'],
                                                           u'type': u'set::resource',
                                                           u'values': [u'$ref:/finishes/opendesk/standard-birch-ply',
                                                                       u'$ref:/finishes/opendesk/premium-birch-ply']}},
                                  u'type': u'string',
                                  u'value': u'birch-ply'},
                                 {u'description': u'...',
                                  u'image': {u'asset': u'../assets/publish/lean_logo.png'},
                                  u'name': u'Standard Laminate',
                                  u'options': {
                                      u'colour': {
                                          u'default': u'white',
                                                           u'description': u'Choose a colour',
                                                           u'name': u'Colour',
                                                           u'type': u'set::string',
                                                           u'values': [{u'b': u'0',
                                                                        u'g': u'255',
                                                                        u'name': u'White',
                                                                        u'r': u'0',
                                                                        u'type': u'string',
                                                                        u'value': u'white'}]
                                      },
                                        u'finish': {u'default': u'/finishes/opendesk/standard-laminate',
                                                   u'scopes': [u'maker'],
                                                   u'type': u'set::resource',
                                                   u'values': [u'$ref:/finishes/opendesk/standard-laminate']
                                        }
                                  },
                                  u'type': u'string',
                                  u'value': u'standard-laminate'},
                                 {u'description': u"Wild and whacky stuff that you'll talk to the maker about",
                                  u'images': [{u'asset': u'../assets/publish/lean_logo.png'}],
                                  u'name': u'Custom Lamination',
                                  u'options': {u'finish': {u'default': u'/finishes/opendesk/custom-lamination',
                                                           u'scopes': [u'maker'],
                                                           u'type': u'set::resource',
                                                           u'values': [u'$ref:/finishes/opendesk/custom-lamination']}},
                                  u'type': u'string',
                                  u'value': u'custom-lamination'}]}
            }
        }

        winnow.validate(doc)


    #
    # def test_breaking_spec(self):
    #
    #     doc = {
    #         u"schema": u"https://opendesk.cc/schemata/options.json",
    #         u"type": u"option",
    #         u"options":{
    #             u"size":{u'default': u'birch-ply',
    #  u'description': u'Choose a material',
    #  u'name': u'Material',
    #  u'type': u'set::string',
    #  u'values': {u'description': u'...',
    #              u'images': [{u'asset': u'../assets/publish/lean_logo.png',
    #                           u'type': u'banner'}],
    #              u'name': u'Birch Ply',
    #              u'options': {u'finish': {u'default': u'$ref:/finishes/opendesk/premium-birch-ply',
    #                                       u'scopes': [u'maker'],
    #                                       u'type': u'set::resource',
    #                                       u'values': {u'changes': u'Initial version',
    #                                                   u'description': u'Highest quality retail-grade birch-ply with two stage fine finishing.',
    #                                                   u'name': u'Premium Birch Plywood',
    #                                                   u'options': {
    #                                                       u'processes': [
    #                                                           {
    #                                                               u'changes': u'Initial version',
    #                                                                                    u'description': u'',
    #                                                                                    u'name': u'Fine Sanding',
    #                                                                                    u'options': {},
    #                                                                                    u'path': u'/processes/opendesk/fine-sanding',
    #                                                                                    u'schema': u'https://opendesk.cc/schemata/process.json',
    #                                                                                    u'source': u'https://opendesk.herokuapp.com/api/v1/open',
    #                                                                                    u'type': u'process',
    #                                                                                    u'version': [1,
    #                                                                                                 0,
    #                                                                                                 0]
    #                                                           },
    #                                                           {
    #                                                               u'changes': u'Initial version',
    #                                                                                    u'description': u'',
    #                                                                                    u'name': u'Oiling',
    #                                                                                    u'options': {},
    #                                                                                    u'path': u'/processes/opendesk/oiling',
    #                                                                                    u'schema': u'https://opendesk.cc/schemata/process.json',
    #                                                                                    u'source': u'https://opendesk.herokuapp.com/api/v1/open',
    #                                                                                    u'type': u'process',
    #                                                                                    u'changes': u"initial version",
    #                                                                                    u'version': [1,
    #                                                                                                 0,
    #                                                                                                 0]
    #                                                           }
    #                                                     ]
    #                                                   },
    #                                                   u'path': u'/finishes/opendesk/premium-birch-ply',
    #                                                   u'schema': u'https://opendesk.cc/schemata/finish.json',
    #                                                   u'source': u'https://opendesk.herokuapp.com/api/v1/open',
    #                                                   u'type': u'finish',
    #                                                   u'version': [1,
    #                                                                0,
    #                                                                0]}}},
    #              u'type': u'string',
    #              u'value': u'birch-ply'}}
    #         }
    #     }
    #
    #     winnow.validate(doc)



    def test_breaking_spec(self):

        doc = {
            "files": {
                "large-1": {
                    "asset": "https://m2.smartdesk.cc/03103/0328/LYT_STD_LRG_AP_cad-1_18.00-0.00.dxf",
                    "name": "Large",
                    "num_sheets": 1
                },
                "medium-2": {
                    "asset": "https://m1.smartdesk.cc/03104/0328/LYT_STD_MED_AP_cad-1_18.00-0.00.dxf",
                    "name": "Medium",
                    "num_sheets": 1
                },
                "small-3": {
                    "asset": "https://m2.smartdesk.cc/03105/0328/LYT_STD_SML_AP_cad-1_18.00-0.00.dxf",
                    "name": "Small",
                    "num_sheets": 1
                }
            },
            "fileset": "/ranges/tetrad/layout-table/standard-public/miy-download@1.0.1",
            "manufacturing": {
                "cutting": {
                    "total_sheets": 3
                },
                "strategies": {
                    "A": {
                        "options": {
                            "sheet-1": {
                                "options": {
                                    "material": {
                                        "$ref": "/materials/opendesk/sheets",
                                        "override": False
                                    }
                                },
                                "sheet": "$ref:~/files/large-1",
                                "type": "string",
                                "value": "large-1"
                            },
                            "sheet-2": {
                                "options": {
                                    "material": {
                                        "$ref": "/materials/opendesk/sheets",
                                        "override": False
                                    }
                                },
                                "sheet": "$ref:~/files/medium-2",
                                "type": "string",
                                "value": "medium-2"
                            },
                            "sheet-3": {
                                "options": {
                                    "material": {
                                        "$ref": "/materials/opendesk/sheets",
                                        "override": False
                                    }
                                },
                                "sheet": "$ref:~/files/small-3",
                                "type": "string",
                                "value": "small-3"
                            }
                        },
                        "type": "string",
                        "value": "A"
                    }
                },
                "units": "mm"
            },
            "options": {
                "material-choices": {
                    "default": "birch-ply",
                    "description": "Choose a material",
                    "name": "Material",
                    "type": "set::string",
                    "values": {
                        "description": "...",
                        "images": [
                            {
                                "asset": "../assets/publish/lean_logo.png",
                                "type": "banner"
                            }
                        ],
                        "name": "Birch Ply",
                        "options": {
                            "finish": {
                                "default": "$ref:/finishes/opendesk/premium-birch-ply",
                                "scopes": [
                                    "maker"
                                ],
                                "type": "set::resource",
                                "values": {
                                    "changes": "Initial version",
                                    "description": "Highest quality retail-grade birch-ply with two stage fine finishing.",
                                    "name": "Premium Birch Plywood",
                                    "options": {
                                        "material": {
                                            "changes": "Initial version",
                                            "description": "Birch-faced natural plywood.",
                                            "name": "Birch Faced Plywood",
                                            "options": {

                                                "strategy": {
                                                    "default": "A",
                                                    "scopes": [
                                                        "maker",
                                                        "operator"
                                                    ],
                                                    "type": "set::string",
                                                    "values": "$ref:~/manufacturing/strategies/A"
                                                }
                                            },
                                            "path": "/materials/opendesk/sheets/wood/composite/plywood/birch-faced-plywood",
                                            "schema": "https://opendesk.cc/schemata/material.json",
                                            "source": "https://opendesk.herokuapp.com/api/v1/open",
                                            "type": "material",
                                            "version": [
                                                1,
                                                0,
                                                0
                                            ]
                                        },
                                        "processes": [
                                            {
                                                "changes": "Initial version",
                                                "description": "",
                                                "name": "Oiling",
                                                "options": {},
                                                "path": "/processes/opendesk/oiling",
                                                "schema": "https://opendesk.cc/schemata/process.json",
                                                "source": "https://opendesk.herokuapp.com/api/v1/open",
                                                "type": "process",
                                                "version": [
                                                    1,
                                                    0,
                                                    0
                                                ]
                                            },
                                            {
                                                "changes": "initial version",
                                                "description": "",
                                                "name": "Fine Sanding",
                                                "options": {},
                                                "path": "/processes/opendesk/fine-sanding",
                                                "schema": "https://opendesk.cc/schemata/process.json",
                                                "source": "https://opendesk.herokuapp.com/api/v1/open",
                                                "type": "process",
                                                "version": [
                                                    1,
                                                    0,
                                                    0
                                                ]
                                            }
                                        ]
                                    },
                                    "path": "/finishes/opendesk/premium-birch-ply",
                                    "schema": "https://opendesk.cc/schemata/finish.json",
                                    "source": "https://opendesk.herokuapp.com/api/v1/open",
                                    "type": "finish",
                                    "version": [
                                        1,
                                        0,
                                        0
                                    ]
                                }
                            }
                        },
                        "type": "string",
                        "value": "birch-ply"
                    }
                },
                "quantity": {
                    "default": 1,
                    "max": 100,
                    "min": 1,
                    "name": "Quantity",
                    "type": "numeric::range"
                }
            },
            "product": "/ranges/tetrad/layout-table/standard-public@1.0.0",
            "schema": "https://opendesk.cc/schemata/manufacturing_specification.json",
            "type": "manufacturing_specification"
        }

        winnow.validate(doc)












