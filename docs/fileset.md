---
layout: default
---

# fileset

A set of files that are useful for making all or a subset of a product family

common resource attributes:

+ **schema** *(string, required)* - Must be ```https://opendesk.cc/schemata/fileset.json```.
+ **type** *(string, required)* - Must be ```fileset```.
+ **source** *(required)* - A base URI that when join with the path gives the canonical identity for this document. The document may or may not be available for download from the resulting URI.
+ **base** *(optional)* - An optional base URL that when joined to the path gives a URL that this document can be downloaded from. 
+ **path** *(string, required)* - A URI identifier.
+ **name** *(string, required)* - A display name.
+ **description** *(string, required)* - A short description.
+ **long_description** *(string, optional)* - A long description.
+ **shortcode** *(string, optional)* - A short capitalised string identifier for the range.
+ **version** *(list, required)* - A list of three integers giving the major, minor and patch version of this document.
+ **image_uri** *(object, optional)* - A reference to an image used to represent this document. An object with a single key ```asset``` and a relative file path. **image_uri** - A reference to an image used to represent this range. Given as an object with a single key "asset" and a value giving a path relative to the location of this document. *(optional)*

fileset attributes:
+ **options** *(object, required)* - A set of options that define the subset of product variations this fileset is for.
+ **category** *(string, required)* - The category of file in this fileset
+ **files** *(list, required)* - A list of the files in the form ```{"asset": <relative file path>}```

This is an example:

```json
{
    "schema": "https://opendesk.cc/schemata/fileset.json",
    "type": "fileset",
    "path": "/ranges/lean/cafe-table/standard/test_fileset_1",
    "source": "https://github.com/opendesk/collection",
    "base": "https://raw.github.com/opendesk/collection/master",
    "category": "sheets", 
    "description": "Cad files for 18mm ply",
    "files": [{"asset": "files/test_1.dxf"},
        {"asset": "files/test_2.dxf"}
    ], 
    "name": "Test Fileset",
    "version": [1, 0, 1],
    "options": {
        "material": "wisa",
        "sheet": "18",
        "thickness": 17.9,
        "tolerance": 0
    }
}
```

The path attribute defines the parent product the fileset is for. For example in the example above this fileset is for the product ```/ranges/lean/cafe-table/standard```

The options attribute defines a subset of the product options space that it applies to. This options set is used when searching for a fileset that matches a particular quantified configuration. The options of a fileset may also introduce new option keys that are not specified in the product json, in fact this is common, for example manufacturing considerations such as ```"tolerance"``` may be introduced.

In the OpenDesk in house publishing system the filesets are generated semi-automatically by looking at the files in the folder.  All you have to do is define a minimal fileset.json with a version number.

```json
{
    "version": [1, 0, 0]
}
```

All resource files below this file will be gathered into filesets for each folder, the details filled in and then published. You can optionally add descriptions

```json
{
    "version": [1, 0, 0],
    "description": "Nice CAD files.."
}
```


