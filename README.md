# winnow

Tools for publishing and manipulating families of products

Winnow is a specification for a json interchange format for publishing information about families of related and configurable products, and a python implementation for manipulating these documents.

winnnow has three distinct uses: 
+ Validation of winnow json documents.
+ Set based operations for comparing and combining winnow document options.
+ Searching winnow documents based on matching document options.

## Validation

To validate a winnow json document simply call ```winnow.validate(doc)``` where doc is a dict obtained by loading the document json. eg:

```python
with open(os.path.join("path/to/json"), "r") as f:
    try:
        winnow.validate(json.loads(f.read()))
    except winnow.OptionsExceptionFailedValidation, e: 
        print "Failed winnow validation %s" % e
```

There are several distinct classes of object defined by winnow's json schemata:

+ **range** - A collection of related designs with common authorship.
+ **design** - An individual design.
+ **product** - A product family. ie a set of variants of the design that share configurable properties.
+ **fileset** - A collection of binary files, such as CAD files or images, related to products.
+ **material** - A material that can be used in making a product.
+ **process** - A process carried out in the making of a product.
+ **finish** - A combination of material and processes that define the finish of a product.

## Operations
