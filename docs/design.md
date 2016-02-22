---
layout: default
---

# design

A design

Common resource attributes:

+ **schema** *(string, required)* - Must be ```https://opendesk.cc/schemata/design.json```.
+ **type** *(string, required)* - Must be ```design```.
+ **source** *(required)* - A base URI that when join with the path gives the canonical identity for this document. The document may or may not be available for download from the resulting URI.
+ **base** *(optional)* - An optional base URL that when joined to the path gives a URL that this document can be downloaded from. 
+ **path** *(string, required)* - A URI identifier.
+ **name** *(string, required)* - A display name.
+ **description** *(string, required)* - A short description.
+ **long_description** *(string, optional)* - A long description.
+ **shortcode** *(string, optional)* - A short capitalised string identifier for the range.
+ **version** *(list, required)* - A list of three integers giving the major, minor and patch version of this document.
+ **image_uri** *(object, optional)* - A reference to an image used to represent this document. An object with a single key ```asset``` and a relative file path.

This is an example:

```json
{
    "schema": "https://opendesk.cc/schemata/design.json",
    "type": "design",
    "path": "/ranges/lean/cafe-table",
    "source": "https://github.com/opendesk/collection",
    "base": "https://raw.github.com/opendesk/collection/master",
    "version": [0,0,1],
    "name": "Cafe Table",
    "shortcode": "CAF",
    "description": "A nice cafe table with three legs"
}
```

A design belongs to a range and the path value must refer to it. ie In the example above the parent range ```/ranges/lean``` must exist.

 




