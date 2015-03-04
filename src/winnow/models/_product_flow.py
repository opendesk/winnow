import time
import json

from _base_sieve import json_dumps
from _product_sieve import ProductSieve
from _fileset_sieve import FilesetSieve
from _context_sieve import ContextSieve
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

    return ProductSieve.publish(db, product_json)


"""
2. CAD files published
  - validate (the fileset documents)
  - allows (check the fileset docs are allowed by their products)
  -> inputs: fileset documents, products
  => outputs: fileset documents
"""
def publish_fileset(db, fileset_json):

    return FilesetSieve.publish(db, fileset_json)


"""
3. API is queried for configuration options
  - merge (context filters are applied to the product model)
  - extract (configuration option subset from merged document)
  -> inputs: context filters, products
  => outputs: configuration options[, merged document?]
"""

def publish_context(db, context_json):

    return ContextSieve.publish(db, context_json)


def get_contextualised_product(db, product_uri, context_uris, extractions=None):

    product_json = db.get(product_uri)
    if product_json is None:
        raise ProductExceptionLookupFailed("get_configuration_options: Couldn't find product %s" % product_uri)

    product = ProductSieve.from_json(product_json)
    return product.merge_and_extract(db, context_uris, extractions=extractions)


def get_configuration_json(db, product_uri, context_uris):

    contextualised_product = get_contextualised_product(db, product_uri, context_uris, extractions=[u"color", u"material"])
    return json_dumps(contextualised_product.doc)



"""
4. customer makes configuration choices
  - validate (the choice document)
  - merge (context filters are applied to the product model)
  - allows (check the choice document against the merged document)
  -> inputs: choice document, context filters, products
  => outputs: choice document, quantified configuration

"""


def get_quantified_configuration(db, choice_json, context_uris, quantity):

    choices = ProductSieve.from_doc(choice_json)
    canonical_product = choices.canonical(db)
    snapshot = canonical_product.take_snapshot(db)

    if not snapshot.allows(choices):
        raise ProductExceptionFailedValidation

    configured_product = snapshot.merge(choices)
    configured_product.doc[u"quantity"] = quantity
    quantified_configuration = configured_product.merge_and_extract(db, context_uris)
    quantified_configuration.save(db)
    return quantified_configuration


"""
5. general file set lookup
  - for each quantified configuration:
    - match (filesets that match the quantified configuration)
  -> inputs: quantified configuration, fileset model
  => outputs: filesets[, relevance info about them?]
"""


def find_file_sets(db, quantified_configuration_uri, context_uris):

    quantified_configuration_json = db.get(quantified_configuration_uri)
    if quantified_configuration_json is None:
        raise ProductExceptionLookupFailed("find_file_sets: Couldn't find quantified_configuration %s" % quantified_configuration_uri)

    quantified_configuration = ProductSieve.from_json(quantified_configuration_json)
    return quantified_configuration.matching_filesets(db, context_uris)
































