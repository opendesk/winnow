# product

A product is a family of versions of a design that are defined by a set of options.

Validated by the schema ```https://opendesk.cc/schemata/product.json``` a product has the following attributes:

+ **schema** - Must be ```https://opendesk.cc/schemata/product.json``` *(required)*
+ **type** - Must be ```product``` *(required)*
+ **source** - A base URI that when join with the path gives the canonical identity for this document. The document may or may not be available for download from the resulting URI  *(required)*
+ **base** - An optional base URL that when joined to the path gives a URL that this document can be downloaded from. *(optional)*
+ **path** - A URI identifier. *(required)*
+ **name** - A display name. *(required)*
+ **description** - A short description of the product. *(required)*
+ **long_description** - A long description of the product. *(optional)*
+ **shortcode** - A short capitalised string identifier for the product. *(optional)*
+ **version** - A list of three integers giving the major, minor and patch version of this document. *(required)*
+ **image_uri** - A reference to an image used to represent this product. Given as an object with a single key "asset" and a value giving a path relative to the location of this document. *(required)*
+ **upstream** - A reference to another product from which this product inherits. *(optional)*
+ **options** - A set of options that define a variety of possible configurations for this product. *(required)*
+ **is_default** - A bool showing if this product is the default for a design. *(optional)*
+ **is_public** - A bool indicating whether this product is visible to the public. *(optional)*

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





