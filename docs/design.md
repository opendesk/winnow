# design

A design

Validated by the schema ```https://opendesk.cc/schemata/design.json``` the design has the following attributes:

+ **schema** - Must be ```https://opendesk.cc/schemata/design.json``` *(required)*
+ **type** - Must be ```design``` *(required)*
+ **source** - A base URI that when join with the path gives the canonical identity for this document. The document may or may not be available for download from the resulting URI  *(required)*
+ **base** - An optional base URL that when joined to the path gives a URL that this document can be downloaded from. *(optional)*
+ **path** - A URI identifier. *(required)*
+ **name** - A display name. *(required)*
+ **description** - A description of the Range that can contain markdown links. *(required)*
+ **shortcode** - A short capitalised string identifier for the design. *(required)*
+ **version** - A list of three integers giving the major, minor and patch version of this document. *(required)*
+ **image_uri** - A reference to an image used to represent this range. Given as an object with a single key "asset" and a value giving a path relative to the location of this document. *(optional)*

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
    "description": "A nice cafe table with three legs"
}
```




