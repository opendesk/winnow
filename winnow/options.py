import collections
from copy import deepcopy

from winnow.values import value_factory
from winnow.exceptions import OptionsExceptionFailedValidation, OptionsExceptionEmptyOptionValues, OptionsExceptionLookupFailed

"""

OptionsSet

This is the beef.

all the logical operations on sieves actually happen in their options dict

"""

class OptionsSet(collections.MutableMapping):
    """a dict like object that supports merging, patching etc wraps an existing dict"""

    def __init__(self, d):
        """
        really its just a wrapped around an existing dict
        """
        self.store = d


    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)


    def _merge_values(self, other, key):
        self_values = self.store.get(key)
        other_values = other.store.get(key)
        if self_values is None:
            return other_values
        elif other_values is None:
            return self_values
        else:
            this = value_factory(self_values)
            that = value_factory(other_values)
            intersection = this.intersection(that)
            if intersection == None:
                raise OptionsExceptionEmptyOptionValues("The key %s has no possible values when %s is merged with %s" % (key, self.uri, other.uri))
            return intersection.as_json()


    def _patch_values(self, other, key):
        self_values = self.store.get(key)
        other_values = other.store.get(key)
        if self_values is None:
            return other_values
        else:
            return self_values


    def patch(self, other):
        """
        A union of all keys
        Self values overwrite others
        """
        return self._combine(other, self._patch_values)


    def merge(self, other):
        """
        A union of all keys
        An intersection of values
        """
        return self._combine(other, self._merge_values)


    def _combine(self, other, combine_func):
        """
        Merge or patch and return a new OptionsSet

        """
        options = {}
        for key in self.key_set.union(other.key_set):
            options[key] = combine_func(other, key)
        return OptionsSet(options)


    def intersects(self, other):
        """
        An intersection of keys
        An intersection check on values
        """

        this_keys = self.key_set
        that_keys = other.key_set

        if this_keys is not None and that_keys is not None:
            all_keys = this_keys.intersection(that_keys)
            if all_keys is not None:
                for key in this_keys.intersection(that_keys):
                    this = value_factory(self.store.get(key))
                    that = value_factory(other.store.get(key))
                    if that.isdisjoint(this):
                        return False

        return True


    def allows(self, other):
        """
        An intersection of keys
        A subset check on values
        """

        this_keys = self.key_set
        that_keys = other.key_set
        if this_keys is not None and that_keys is not None:
            all_keys = this_keys.intersection(that_keys)
            if all_keys is not None:
                for key in this_keys.intersection(that_keys):
                    this = value_factory(self.store.get(key))
                    that = value_factory(other.store.get(key))
                    if not that.issubset(this):
                        return False
        return True


    def extract(self, key_names):
        """
        extracts a subset of options by key
        """
        options = {}
        for key in self.key_set:
            if key in key_names:
                options[key] = deepcopy(self.store[key])
        return OptionsSet(options)


    def match(self, others):
        return [other for other in others if self.allows(other)]

    def match_intersects(self, others):
        return [other for other in others if self.intersects(other)]

    def reverse_match(self, others):
        return [other for other in others if other.allows(self)]


    @property
    def key_set(self):
        return set(self.store.keys())


