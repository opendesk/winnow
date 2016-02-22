---
layout: default
---

# winnow document structure

Winnow documents always have the following information which provides basic information about identity.

+ **schema** *(string, required)* - The schema that describes this document's structure
+ **type** *(string, required)* - The type name of this document
+ **name** *(string, required)* - A display name.
+ **description** *(string, required)* - A short description.
+ **long_description** *(string, optional)* - A long description.
+ **images** *(array, optional)* - A array of images. Each is an object with the key ```asset``` giving a relative file path and ```type``` giving further usage information.

Resources documents also have these additional attributes, which provide information about its position in a set of cannonical resources.

+ **source** *(required)* - A base URI that when joined with the path gives the canonical identity for this document. The document may or may not be available for download from the resulting URI.
+ **base** *(optional)* - An optional base URL that when joined to the path gives a URL that this document can be downloaded from. 
+ **path** *(string, required)* - A URI identifier.
+ **shortcode** *(string, optional)* - A short capitalised string identifier that can serve as an alias for the resource.
+ **version** *(list, required)* - A list of three integers giving the major, minor and patch version of this document.
+ **changes** *(string, required)* - A description of how this version has changed from the previous one.

And many documents also have an options field that contains all the information about options and choices

 **options** *(object, optional)* - A set of options that describe possible variations of this resource.
 
 You can read more about [how options work](options.html)
 
 
 
 