# winnow

Winnow is a json exchange format for publishing families of configurable products. It has several distinct parts:

+ Json schemas for documents describing products and associated information.
+ A schema for defining sets of configuration options.
+ A defined set of basic logical operations for manipulating documents with options.
+ A python library that implements these operations

In order to write and publish winnow documents you use the first two of these as they define how winnow documents are constructed. To apply logical operations to, and manipulate, winnow documents you will need to understand winnow's operations and it's library that implements them.


## resources

Eight resource types for publishing are currently defined in winnow. Follow links to see their full descriptions.

+ [*range*](range.md) - A collection of related designs with common authorship
+ [*design*](design.md) - A design
+ *product* - A family of versions of a design defined by a common set of options
+ *fileset* - A set of files that are useful for making all or a subset of a product family
+ *finish* - A finish for a product defined by a set of materials and processes
+ *material* - A material
+ *process* - A process that is applied to a material
+ *context* - An collection of options used to filter or extend a product's options

Resources have certain features:
 
They are a named resource, discoverable at a permanent url defined within the document.
They are versioned and use Semantic Version numbers.
Versions are discoverable at a permanent url.
They may inherit from another resource of the same type.

Winnow also defines two document types that are not named resources, but are created as intermediate files during processing:

+ *choice*
+ *quantified_configuration*

## validation

In winnow.schemata there are json schemas that can be used to validate winnow documents. This can be done using tools available from [json-schema.org](http://json-schema.org/implementations.html), or using winnow's python library like this:

```python
    with open(filepath, "r") as f:
        doc = json.loads(f.read())
        winnow.validate(doc)
```


## options

Some winnow documents have a top level ```options``` attribute.  This object describes a related family of products by defining a set of possible configurations for a product, for example available colours or sizes. 

 ```json
 {
    "options":{
        "colour": ["red", "blue", "green"],
        "size": ["big", "small],
        "wheels": [4, 6]
     }
     ...
 }
 ```

This describes the product family for a toy that comes in three colours, two sizes and can have either four or six wheels. Winnow provides both a json language for defining these options and a set of operations for manipulating them.

You can read more about winnow's values here [options](options.md)

## operations

Winnow defines a set of simple, but powerful, operations to help manipulate winnow documents.

+ *add_doc* 
+ *allows*
+ *intersects*
+ *merge*
+ *patch*
+ *scope*
+ *filter_allows*
+ *filter_allowed_by*
+ *inline*
+ *expand*
+ *asset_paths*
+ *validate*

## library











