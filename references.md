---
layout: default
---

# references

Winnow makes extensive use of JSONPath style references within its documents. 
A reference looks like `$ref:/materials/opendesk/sheets/wood/composite/plywood/birch-faced-plywood`

References can be used to create composite documents that re-use other documents. 
For example here the values of a set::string option are strings that reference other documents.

```json
    "options": {
        "material": {
            "type": "set::string", 
            "values": "$ref:/materials/opendesk/sheets/wood/composite/plywood/birch-faced-plywood"
        }, 
        "processes": {
            "options": {
                "oiling": "$ref:/processes/opendesk/oiling", 
                "sanding": "$ref:/processes/opendesk/fine-sanding"
            }, 
            "type": "set::string", 
            "value": "finishing-processes"
        }
    }, 
```


You can also reference portions of other documents using JSONPath's xpath style annotation. 
Here the options for `material-choices` are copied in from the context `/contexts/opendesk/standard-materials` :

```json 
    "options": {
        "material-choices": "$ref:/contexts/opendesk/standard-materials~/options/material-choices"
    }, 
```


It's also possible to include a subset of another document by using an options key along with a reference. 
Here a specific thickness of plywood is targeted in the document `/sizes/opendesk/1220-x-2440-mm`

```json
"size": {
    "type": "set::resource", 
    "values": [
        {
            "$ref": "/sizes/opendesk/1220-x-2440-mm", 
            "options": {
                "thickness": {
                    "type": "numeric::number", 
                    "value": 18.0
                }
            }
        }
    ]
}
```


