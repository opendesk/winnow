
from base_values import BaseWinnowValue
from winnow.exceptions import OptionsExceptionFailedValidation
from winnow.constants import *
from winnow.utils import json_dumps
from copy import deepcopy

class OptionWinnowValue(BaseWinnowValue):


    def __init__(self, value=None):

        super(OptionWinnowValue, self).__init__(value)

        if isinstance(value, dict):
            self.set_my_values(value.get(VALUES_KEY_NAME))

        else:
            self.set_my_values(value)


    def __len__(self):
        return len(self.values_lookup)


    def _get_value_options(self, value_id):
        value = self.values_lookup.get(value_id)
        if isinstance(value, unicode):
            return None
        return value.get(u"options")


    def is_determined(self):
        if isinstance(self.value, list):
            return False
        elif isinstance(self.value, unicode):
            return True
        elif isinstance(self.value, dict):
            return True




    @classmethod
    def from_value(cls, value):

        if isinstance(value, list):
            try:
                string_list = [unicode(v) for v in value]
            except:
                raise OptionsExceptionFailedValidation("OptionStringSieveValue unrecognised value type")
            # numeric = NumericSetSieveValue.make(decimal_list)


            option = OptionStringWinnowValue(string_list)
            if option is None:
                raise OptionsExceptionFailedValidation("OptionSieveValue: empty set")
            return option

        elif isinstance(value, dict):
            option_type = value[u"type"]
            if option_type == VALUE_TYPE_SET_STRING:
                return OptionStringWinnowValue(value)
            elif option_type == VALUE_TYPE_SET_COLOUR:
                return OptionStringWinnowValue(value)
            elif option_type == VALUE_TYPE_SET_SIZE:
                return OptionStringWinnowValue(value)
            elif option_type == VALUE_TYPE_SET_RESOURCE:
                return OptionResourceWinnowValue(value)
            elif option_type == VALUE_TYPE_SET_NULL:
                return OptionNullWinnowValue(value)
            else:
                raise OptionsExceptionFailedValidation("OptionSieveValue unrecognised value type")
        elif value is None:
            return OptionNullWinnowValue(value)
        else:
            try:
                s = unicode(value)
            except:
                raise OptionsExceptionFailedValidation("OptionSieveValue unrecognised value type")

            return OptionStringWinnowValue(s)


    def set_my_values(self, list_or_single):

        if isinstance(list_or_single, list):
            # for v in list_or_single:
            #     if isinstance(v, dict):
            #         if not v.get(u"type") == self.type:
            #             print "type", v.get(u"type"), self.type
            #             raise OptionsExceptionFailedValidation("OptionSieveValue unrecognised value type")
            self._set_value_list(list_or_single)
            if len(list_or_single) ==  0:
                raise Exception("null string value")
            elif len(list_or_single) == 1:
                first = list_or_single[0]
                self.values = first
            else:
                self.values = list_or_single
        else:
            self._set_value_list([list_or_single])
            self.values = list_or_single

    def as_json(self):

        values = self.values

        ## return the value without metadata is there is none
        if self.name is None and self.scopes is None and self.description is None and self.image_url is None:
            return values


        ## otherwise wrap it in a dict
        value =  {
            u"type": self.type,
            VALUES_KEY_NAME: values,
        }

        return self.update_with_info(value)



class OptionStringWinnowValue(OptionWinnowValue):

    type = VALUE_TYPE_SET_STRING

    def validate_single_value(self, value):
        if not isinstance(value, unicode):
            raise Exception("should be unicode %s" % value)


    def __str__(self):
        return str(self.as_json())


    def _set_value_list(self, value_list):

        self.values_lookup = {}
        for v in value_list:
            try:
                single_value = v if isinstance(v, unicode) else v[u"value"]
            except KeyError:
                single_value = v if isinstance(v, unicode) else v[u"path"]

            self.validate_single_value(single_value)
            self.values_lookup[single_value] = v


    def get_default(self):
        return self._default if self._default is not None else self.values_lookup.keys()[0]

    @property
    def default(self):
        from winnow.options import OptionsSet

        default_string = self._default if self._default is not None else self.values_lookup.keys()[0]
        default_value = self.values_lookup[default_string]
        new_value = deepcopy(default_value)
        value_options = new_value.get(u"options")

        if value_options is None or value_options == {}:
            return default_string
        else:
            new_value[u"options"] = OptionsSet(value_options).default().store

        info = self.get_merged_info(self)
        info[u"type"] = self.type,
        info[VALUES_KEY_NAME] = [new_value]

        return self.__class__(info).as_json()


    def isdisjoint(self, other):
        if isinstance(other, OptionNullWinnowValue):
            return False
        self.check_class(other)
        other_keys = set(other.values_lookup.keys())
        self_keys = set(self.values_lookup.keys())
        return self_keys.isdisjoint(other_keys)


    def issubset(self, other):
        if isinstance(other, OptionNullWinnowValue):
            return True
        from winnow.options import OptionsSet
        self.check_class(other)
        other_keys = set(other.values_lookup.keys())
        self_keys = set(self.values_lookup.keys())

        ## check this values keys
        if not self_keys.issubset(other_keys):
            return False

        ## if self and other have matching values that both have have nested options check them too
        for key in self_keys:
            this_options = self._get_value_options(key)
            that_options = other._get_value_options(key)
            if this_options is not None and that_options is not None:
                if not OptionsSet(that_options).allows(OptionsSet(this_options)):
                    return False
        return True


    def intersection(self, other):

        from winnow.options import OptionsSet

        self.check_class(other)

        values = []

        if isinstance(other, OptionNullWinnowValue):

            other_options = other._get_options()
            if other_options is None:
                return self

            self_keys = list(self.values_lookup.keys())

            for value_id in self_keys:
                this_value = self.values_lookup.get(value_id)
                if isinstance(this_value, dict):
                    new_value = deepcopy(this_value)
                    this_options = self._get_value_options(value_id)
                elif isinstance(this_value, unicode):
                    new_value = {
                        "type": u"string",
                        "value": this_value
                    }
                    this_options = None
                else:
                    raise Exception("This shouldn't ever happen")

                if this_options is not None:
                    new_value[u"options"] = OptionsSet(this_options).merge(OptionsSet(other_options)).store

                values.append(new_value)

        else:
            other_keys = list(other.values_lookup.keys())
            self_keys = list(self.values_lookup.keys())
            other_keys.sort()


            # find matching values

            # get the one to use

            # add them to the list

            ## when putting together the intersecting values perform a merge on their nested options
            for value_id in other_keys:

                this_value = self.values_lookup.get(value_id)
                if this_value is None:
                    continue
                other_value = other.values_lookup[value_id]

                ## if they are both unicode just add the value
                if isinstance(other_value, unicode) and isinstance(this_value, unicode):
                    values.append(this_value)
                elif isinstance(other_value, unicode) and isinstance(this_value, dict):
                    values.append(deepcopy(this_value))
                elif isinstance(other_value, dict) and isinstance(this_value, unicode):
                    values.append(deepcopy(other_value))
                elif isinstance(other_value, dict) and isinstance(this_value, dict):
                    new_value = self.munge_values(this_value, other_value)
                    values.append(new_value)
                else:
                    raise Exception("this should never happen")

        ## if there is no intersection return None
        if len(values) == 0:
            return None

        info = self.get_merged_info(other)
        info[u"type"] = self.type,
        info[VALUES_KEY_NAME] = values

        return self.__class__(info)

    def _get_options(self, value):
        if isinstance(value, unicode):
            return None
        return value.get(u"options")

    def munge_values(self, this_value, other_value):

        from winnow.options import OptionsSet

        new_value = deepcopy(other_value)
        new_value.update(deepcopy(this_value))
        ## and then merge their options
        this_options = self._get_options(this_value)
        that_options = self._get_options(other_value)

        if this_options is not None and that_options is not None:
            new_value[u"options"] = OptionsSet(this_options).merge(OptionsSet(that_options)).store
        elif this_options is not None or that_options is not None:
            new_value[u"options"] = this_options if this_options is not None else that_options
        else:
            pass

        return new_value
    

class OptionNullWinnowValue(OptionStringWinnowValue):


    def __init__(self, value=None):

        super(OptionWinnowValue, self).__init__(value)
        self.values = value

    type = VALUE_TYPE_SET_NULL

    def intersection(self, other):
        from winnow.options import OptionsSet

        if isinstance(other, OptionNullWinnowValue):

            this_options = self._get_options
            that_options = other._get_options

            options = None

            if this_options is not None and that_options is not None:
                options = OptionsSet(this_options).merge(OptionsSet(that_options)).store
            elif this_options is not None or that_options is not None:
                options = this_options if this_options is not None else that_options
            else:
                pass

            info = self.get_merged_info(other)
            info[u"type"] = self.type,


            if options is not None:

                info[VALUES_KEY_NAME] = {
                    u"options": options
                }

            return self.__class__(info)

        if isinstance(other, OptionResourceWinnowValue) or isinstance(other, OptionStringWinnowValue):
            return other.intersection(self)

        return None




    def isdisjoint(self, other):
        return False

    def issubset(self, other):
        return isinstance(other, OptionNullWinnowValue)


    def _get_options(self):
        if isinstance(self.values, dict) and u"options" in self.values.keys():
            return self.values[u"options"]
        return None



    def as_json(self):

        options = self._get_options()

        if options is None:
            return None

        # values = None
        #
        # ## return the value without metadata is there is none
        # if self.name is None and self.scopes is None and self.description is None and self.image_url is None:
        #     return values

        ## otherwise wrap it in a dict
        value =  {
            u"type": self.type,
            u"options": options,
        }


        return value




class OptionResourceWinnowValue(OptionStringWinnowValue):

    type = VALUE_TYPE_SET_RESOURCE

    @classmethod
    def from_value(cls, value):

        return OptionResourceWinnowValue(value)


    @staticmethod
    def _are_related_in_taxonomy(path_a, path_b):
        return path_a == path_b or path_a.startswith(path_b) or path_b.startswith(path_a)


    @staticmethod
    def _prune_child_nodes(paths):
        passed = []
        for path_a in paths:
            if not any(p for p in paths if path_a.startswith(p) and p != path_a):
                passed.append(path_a)
        return passed

    @staticmethod
    def _nearest_match(path, paths):

        match = None
        for other_path in paths:
            if len(other_path) <= len(path) and path.startswith(other_path) and (match is None or len(other_path) > len(match)):
                match = other_path
        return match


    @staticmethod
    def _intersection_of_path_sets(paths_a, paths_b):
        passed = []
        for path_a in paths_a:
            if any(p for p in paths_b if path_a.startswith(p)):
                if not path_a in passed:
                    passed.append(path_a)
        for path_b in paths_b:
            if any(p for p in paths_a if path_b.startswith(p)):
                if not path_b in passed:
                    passed.append(path_b)
        return passed



    def issubset(self, other):

        if isinstance(other, OptionNullWinnowValue):
            return False

        if not self.__class__ == other.__class__:
            raise Exception("types must match")

        other_paths = set(other.values_lookup.keys())
        self_paths = set(self.values_lookup.keys())

        # each path must find itself or parent in other
        for p1 in self_paths:
            if not any(p2 for p2 in other_paths if p1.startswith(p2)):
                return False
        return True


    def isdisjoint(self, other):
        if isinstance(other, OptionNullWinnowValue):
            return False

        if not self.__class__ == other.__class__:
            raise Exception("types must match")

        other_paths = set(other.values_lookup.keys())
        self_paths = set(self.values_lookup.keys())

        for p1 in self_paths:
            for p2 in other_paths:
                if self._are_related_in_taxonomy(p1, p2):
                    return False
        return True


    def intersection(self, other):

        # print "doing intersection"

        from winnow.options import OptionsSet

        self.check_class(other)

        values = []

        if isinstance(other, OptionNullWinnowValue):

            other_options = other._get_options()
            if other_options is None:
                return self

            self_keys = list(self.values_lookup.keys())

            for value_id in self_keys:
                this_value = self.values_lookup.get(value_id)
                if isinstance(this_value, dict):
                    new_value = deepcopy(this_value)
                    this_options = self._get_value_options(value_id)
                else:
                    raise Exception("This shouldn't ever happen")

                if this_options is not None:
                    new_value[u"options"] = OptionsSet(this_options).merge(OptionsSet(other_options)).store

                values.append(new_value)

        else:

            # take a cope of the the possible values in a lookup table keyed by path
            all_values = deepcopy(self.values_lookup)
            all_values.update(deepcopy(other.values_lookup))

            # prune and child nodes from each set

            other_paths = list(other.values_lookup.keys())
            self_paths = list(self.values_lookup.keys())

            other_paths_pruned = self._prune_child_nodes(other_paths)
            self_paths_pruned = self._prune_child_nodes(self_paths)

            # then add values if it or parent is in other
            intersecting_paths = self._intersection_of_path_sets(other_paths_pruned, self_paths_pruned)

            # for each intersecting path find the most specific option set on each side and merge them
            values = []

            # print "intersecting_paths", intersecting_paths

            for path in intersecting_paths:
                # find best fit values to get merged options
                this_value = self.values_lookup[self._nearest_match(path, self_paths)]
                other_value = other.values_lookup[self._nearest_match(path, other_paths)]

                # print "this_value", this_value
                # print "other_value", other_value

                merged_value = self.munge_values(this_value, other_value)
                options = merged_value["options"]
                # print "options xxx for %s" % path, options.keys()
                # and then add these options to a copy of the origional value from all_values
                new_value = all_values[path]
                new_value["options"] = options

                values.append(new_value)


        ## if there is no intersection return None
        if len(values) == 0:
            return None

        info = self.get_merged_info(other)
        info[u"type"] = self.type,
        info[VALUES_KEY_NAME] = values

        return self.__class__(info)


class OptionSizeWinnowValue(OptionStringWinnowValue):

    type = VALUE_TYPE_SET_SIZE

class OptionColourWinnowValue(OptionStringWinnowValue):

    type = VALUE_TYPE_SET_COLOUR

