# winnow

Winnow is a json interchange format for publishing families of configurable products. It has several distinct parts:

+ A set of json schemata for documents describing products and associated information.
+ A schema for defining sets of configuration options in products.
+ A defined set of basic logical operations for manipulating documents with options.
+ A python library that implements these operations

In order to write and publish winnow documents you use the first two of these as they define how winnow documents are constructed. To apply logical operations to, and manipulate, winnow documents you will need to understand winnow's operations and it's library that implements them.


## resources and documents

Some winnow documents describe named resources others do not. 

Resource documents have certain features: they are discoverable at a permanent url defined in the document itself; they are versioned and use Semantic Version numbers; these versions are themselves discoverable and resources may inherit from another resource of the same type.

Eight resource types are currently defined in winnow. Follow links to see their full descriptions.

+ [*range*](docs/range.md) - A collection of related designs with common authorship
+ [*design*](docs/design.md) - A design
+ [*product*](docs/product.md) - A family of versions of a design defined by a common set of options
+ [*fileset*](docs/fileset.md) - A set of files that are useful for making all or a subset of a product family
+ *finish* - A finish for a product defined by a set of materials and processes
+ *material* - A material
+ *process* - A process that is applied to a material
+ *context* - An collection of options used to filter or extend a product's options

Winnow also defines two document types that are not named resources, but are created as intermediate files during processing:

+ *choice*
+ *quantified_configuration*

## validation

In winnow.schemata there are json schemata that can be used to validate winnow documents. This can be done using tools available from [json-schema.org](http://json-schema.org/implementations.html), or using winnow's python library like this:

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

You can read more about winnow's values here [options](docs/options.md)

## operations

Winnow defines a set of simple, but powerful, operations to help manipulate winnow documents.

+ *add_doc* 
+ *allows*
+ *merge*
+ *scope*
+ *default_choices*
+ *quantify*
+ *filter_allows*
+ *filter_allowed_by*
+ *is_allowed_by*
+ *expand*
+ *asset_props*
+ *validate*

## library





