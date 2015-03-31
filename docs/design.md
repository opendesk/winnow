# design

A design

Validated by the schema ```https://opendesk.cc/schemata/design.json``` the design has the following attributes:

+ **schema** - Must be ```https://opendesk.cc/schemata/design.json``` *(string - required)*
+ **type** - Must be ```design``` *(string - required)*
+ **source** - A base URI that when join with the path gives the canonical identity for this document. The document may or may not be available for download from the resulting URI  *(string - required)*
+ **base** - An optional base URL that when joined to the path gives a URL that this document can be downloaded from. *(string, optional)*
+ **path** - A URI identifier. *(string - required)*
+ **name** - A display name. *(string - required)*
+ **description** - A short description *(string - required)*
+ **long_description** - A long description *(string - optional)*
+ **shortcode** - A short capitalised string identifier for the range. *(string - optional)*
+ **version** - A list of three integers giving the major, minor and patch version of this document. *(list - required)*
+ **image_uri** - A reference to an image used to represent this range. An object with a single key ```asset``` and a relative filepath *(object - optional)*

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




