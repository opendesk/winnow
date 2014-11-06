
# Document Publishing Steps

* we have six underlying operations that are performed on documents
* these are performed at seven key steps

## Operations

* validate (against a global schema)
* allows (child document meets the rules of parent document)

* match (query to find those that meet the rules of a document)
* extract (a subset of a document)

* merge (union of keys, intersection of values)
* patch (union of keys, child values overwrite parent values)

## Steps

1. product model published
  - validate (the product documents)
  - patch (to expand the child document with the parent graph)
  -> inputs: product documents, upstream product graph
  => outputs: product documents

2. CAD files published
  - validate (the fileset documents)
  - allows (check the fileset docs are allowed by their products)
  -> inputs: fileset documents, products
  => outputs: fileset documents

3. API is queried for configuration options
  - merge (context filters are applied to the product model)
  - extract (configuration option subset from merged document)
  -> inputs: context filters, products
  => outputs: configuration options[, merged document?]

4. customer makes configuration choices
  - validate (the choice document)
  - merge (context filters are applied to the product model)
  - allows (check the choice document against the merged document)
  -> inputs: choice document, context filters, products
  => outputs: choice document, quantified configuration

5. general file set lookup
  - for each quantified configuration:
    - match (filesets that match the quantified configuration)
  -> inputs: quantified configuration, fileset model
  => outputs: filesets[, relevance info about them?]

>>> at this point you may exit to the designer flow

6. lookup makers
  - XXX the main query is SQL find nearest makers
  - XXX what kind of merge to (apply the filesets to the quantified configurations)
  - match (makers against the merged documents)
  -> inputs: location[, filesets, quantified configuration, maker model]
  => outputs: makers

>>> at this point makers can be invited

7. specific fileset lookup for maker
  - for each quantified configuration:
    - merge (country filters and maker capabilities with quantified configuration)
    - match (filesets that match the merged document)
  -> inputs: country filters, maker capabilities, quantified configuration, fileset model
  => outputs: filesets[, relevance info about them?]

>>> at the point the maker uses their own judgement
>>> but *in future* we could inject some cost estimation value add cleverness

8. generate the manufacturing spec:
  - XXX what kind of merge to (apply the filesets to the quantified configurations)
  -> inputs: filesets, quantified configurations
  => outputs: manufacturing spec document

>>> and so on...

***

# N.b.: Also Utility Functions

* expand references
* strip references

