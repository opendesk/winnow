
from sieve.product_exceptions import ProductExceptionFailedValidation



class BaseSieveValue(object):

    def check_class(self, other):
        if not self.__class__ == other.__class__:
            raise Exception("sieve value types must match")













