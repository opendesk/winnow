import time
import json

from product_sieve import ProductSieve
from fileset_sieve import FilesetSieve
from context_sieve import ContextSieve
from product_exceptions import ProductExceptionFailedValidation, ProductExceptionLookupFailed, ProductExceptionNoAllowed

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

TODO

 hashing

 complex values

 value references

 option dependency and extension

"""



"""
1. product model published
  - validate (the product documents)
  - patch (to expand the child document with the parent graph)
  -> inputs: product documents, upstream product graph
  => outputs: product documents
"""

def publish_product(db, product_json):

    product = ProductSieve.from_json(product_json)
    patched = product.patch_upstream(db)
    product.save(db)

"""
2. CAD files published
  - validate (the fileset documents)
  - allows (check the fileset docs are allowed by their products)
  -> inputs: fileset documents, products
  => outputs: fileset documents
"""

def publish_fileset(db, fileset_json, cad_files=None):

    fileset = FilesetSieve.from_json(fileset_json)
    frozen_product = fileset.freeze_product(db)

    if not frozen_product.allows(fileset):
        raise ProductExceptionNoAllowed

    fileset.add_files(db, cad_files)
    fileset.save(db)


"""
3. API is queried for configuration options
  - merge (context filters are applied to the product model)
  - extract (configuration option subset from merged document)
  -> inputs: context filters, products
  => outputs: configuration options[, merged document?]
"""


def publish_context(db, context_json):
    context = ContextSieve.from_json(context_json)
    context.save(db)



def get_contextualised_product(db, product_uri, context_uris, extractions=None):

    product_json = db.get(product_uri)

    if product_json is None:
        raise ProductExceptionLookupFailed("get_configuration_options: Couldn't find product %s" % product_uri)

    product = ProductSieve.from_json(product_json)

    return product.merge_and_extract(db, product, context_uris, extractions)







"""
4. customer makes configuration choices
  - validate (the choice document)
  - merge (context filters are applied to the product model)
  - allows (check the choice document against the merged document)
  -> inputs: choice document, context filters, products
  => outputs: choice document, quantified configuration

"""


def get_quantified_configuration(db, choice_json, context_uris, quantity):

    choice = ProductSieve.from_json(choice_json)
    product = ProductSieve.from_json(db.get(choice.uri))

    if not product.allows(choice):
        raise ProductExceptionFailedValidation

    quantified_configuration = choice.merge_and_extract(db, choice, context_uris)
    quantified_configuration.json_dict[u"quantity"] = quantity

    return quantified_configuration



"""
5. general file set lookup
  - for each quantified configuration:
    - match (filesets that match the quantified configuration)
  -> inputs: quantified configuration, fileset model
  => outputs: filesets[, relevance info about them?]
"""



def find_file_sets(db, quantified_configuration, possible_filesets):

    return quantified_configuration.reverse_match(possible_filesets)
































