import time

from product_sieve import ProductSieve
from product_exceptions import ProductExceptionFailedValidation, ProductExceptionLookupFailed

"""
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

  ******************************************
"""


"""
  use object hash for identity


  verson_no/verson_no/verson_no



  "standard@git_object_hash"

  use git hash for this

  /hash@rev/hash@rev

  range/design


  product/lean/desk/standard.json
  config/lean/desk/
  fileset/lean/desk/ply


  materials/od/wood/cnc


"""

def publish_product(db, product_dict, src_url):
    """
    Publishes a product document to to given db

    - validate (the product documents)
    - patch (to expand the child document with the parent graph)

    Might raise ProductExceptionFailedValidation, ProductExceptionLookupFailed

    :param db: The db to save in and to look for ancestors
    :param product_dict: The Product
    :param src_url: The reference src for this document
    """

    product = ProductSieve(product_dict, src_url)
    ## this does a sanity check on expanding the product
    expanded = product.with_expanded_ancestors(db)


    db.set(product_dict, product.uri)





