# range

A collection of related designs with common authorship.

Common resource attributes:

+ **schema** *(string, required)* - Must be ```https://opendesk.cc/schemata/range.json```.
+ **type** *(string, required)* - Must be ```range```.
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
    "description": "[00](http://project00.net) designed the Lean range through a series of fit out commissions in London. It has a stripped back, warehouse aesthetic, with the designs simplified to the bare essentials.\n\nDesk, the first OpenDesk, was designed with and for leading product development agency [Mint Digital](/case_studies/mint-digital). The Meeting and Cafe tables were developed through the major fit out of the [Hub Westminster](/case_studies/hub-westminster), a 12,000 sqft shared workspace in central London.", 
    "image_uri": {
        "asset": "../assets/publish/lean_logo.png"
    }, 
    "name": "Lean", 
    "path": "/ranges/lean", 
    "schema": "https://opendesk.cc/schemata/range.json", 
    "shortcode": "LEN", 
    "source": "https://github.com/opendesk/collection", 
    "type": "range", 
    "version": [
        0, 
        0, 
        1
    ]
}
```




