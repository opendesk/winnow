# product

A product is a family of versions of a design that are defined by a set of options.

Common resource attributes:

+ **schema** *(string, required)* - URI of schema to validate this document. Must be ```https://opendesk.cc/schemata/product.json```.
+ **type** *(string, required)* - Must be ```product```.
+ **source** *(required)* - A base URI that when join with the path gives the canonical identity for this document. The document may or may not be available for download from the resulting URI.
+ **base** *(optional)* - An optional base URL that when joined to the path gives a URL that this document can be downloaded from. 
+ **path** *(string, required)* - A URI identifier.
+ **name** *(string, required)* - A display name.
+ **description** *(string, required)* - A short description.
+ **long_description** *(string, optional)* - A long description.
+ **shortcode** *(string, optional)* - A short capitalised string identifier for the range.
+ **version** *(list, required)* - A list of three integers giving the major, minor and patch version of this document.
+ **image_uri** *(object, optional)* - A reference to an image used to represent this document. An object with a single key ```asset``` and a relative file path.

product attributes:

+ **upstream** *(string, optional)* - A reference to another product from which this product inherits.
+ **options** *(object, required)* - A set of options that define a variety of possible configurations for this product.
+ **is_default** *(bool, optional)* - A bool showing if this product is the default for a design.
+ **is_public** *(bool, optional)* - A bool indicating whether this product is visible to the public.

This is an example:

```json
{
    "schema": "https://opendesk.cc/schemata/product.json",
    "type": "product",
    "path": "/ranges/lean/cafe-table/standard",
    "source": "https://github.com/opendesk/collection",
    "base": "https://raw.github.com/opendesk/collection/master",
    "version": [0,0,1],
    "name": "Standard Cafe Table",
    "shortcode": "STD",
    "description": "A nice cafe table with three legs",
    "is_default": true,
    "is_public": true,
    "upstream": "/ranges/lean/cafe-table/parent",
    "options":{
        "material": {
            "type": "set::string",
            "name": "Material",
            "description": "Choose one of the materials",
            "values": [
                "/materials/opendesk/sheets/wood/composite/plywood",
                "/materials/opendesk/sheets/wood/composite/plywood/pre-laminated-plywood/wisa-multiwall"
            ]
        },
        "sheet": {
            "type": "set::string",
            "name": "Nominal sheet thickness",
            "description": "The nominal sheet thickness",
            "values": [
                {
                    "type": "string",
                    "name": "18mm",
                    "description": "18mm ply wood",
                    "image_uri": {"asset": "http://something.com/khgfdkyg.png"},
                    "value": "18mm"
                }
            ]
        }
    }
}
```

The syntax for writing the product's ```options``` object is complex and is explained in detail here [options](options.md)





