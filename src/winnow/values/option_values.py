
from base_values import BaseSieveValue
from winnow.exceptions import OptionsExceptionFailedValidation
from winnow.constants import *
from copy import deepcopy

class OptionSieveValue(BaseSieveValue):


    def __init__(self, value):

        if isinstance(value, dict):
            self.uri = value.get("uri")
            self.name = value.get("name")
            self.description = value.get("description")
            self.image_url = value.get("image_url")
            self.set_my_values(value.get(VALUES_KEY_NAME))

        else:
            self.uri = None
            self.name = None
            self.description = None
            self.image_url = None
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
            option = OptionStringSieveValue(string_list)
            if option is None:
                raise OptionsExceptionFailedValidation("OptionSieveValue: empty set")
            return option

        elif isinstance(value, dict):
            option_type = value[u"type"]
            if option_type in (VALUE_TYPE_SET_STRING, VALUE_TYPE_SET_RESOURCE):

                return OptionStringSieveValue(value)
            else:
                raise OptionsExceptionFailedValidation("OptionSieveValue unrecognised value type")
        else:
            try:
                s = unicode(value)
            except:
                raise OptionsExceptionFailedValidation("OptionSieveValue unrecognised value type")

            return OptionStringSieveValue(s)


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
        if self.name is None and self.uri is None and self.description is None and self.image_url is None:
            return values

        ## otherwise wrap it in a dict
        value =  {
            u"type": self.type,
            VALUES_KEY_NAME: values,
        }

        if self.name is not None:
            value[u"name"] = self.name
        if self.uri is not None:
            value[u"uri"] = self.uri
        if self.description is not None:
            value[u"description"] = self.description
        if self.image_url is not None:
            value[u"image_url"] = self.image_url

        return value



class OptionStringSieveValue(OptionSieveValue):

    type = VALUE_TYPE_SET_STRING

    def validate_single_value(self, value):
        if not isinstance(value, unicode):
            raise Exception("should be unicode %s" % value)


    def __str__(self):
        return str(self.values_lookup.keys())


    def _set_value_list(self, value_list):
        self.values_lookup = {}
        for v in value_list:
            try:
                single_value = v if isinstance(v, unicode) else v[u"value"]
            except KeyError:
                single_value = v if isinstance(v, unicode) else v[u"path"]

            self.validate_single_value(single_value)
            self.values_lookup[single_value] = v


    def isdisjoint(self, other):
        self.check_class(other)
        other_keys = set(other.values_lookup.keys())
        self_keys = set(self.values_lookup.keys())
        return self_keys.isdisjoint(other_keys)


    def issubset(self, other):
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

        other_keys = list(other.values_lookup.keys())
        self_keys = list(self.values_lookup.keys())
        other_keys.sort()

        values = []

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
                ##prefer this's values over that's
                new_value = deepcopy(other_value)
                new_value.update(deepcopy(this_value))
                ## and then merge their options
                this_options = self._get_value_options(value_id)
                that_options = other._get_value_options(value_id)

                if this_options is not None and that_options is not None:
                    new_value[u"options"] = OptionsSet(this_options).merge(OptionsSet(that_options)).store
                elif this_options is not None or that_options is not None:
                    new_value[u"options"] = this_options if this_options is not None else that_options
                else:
                    pass

                values.append(new_value)
            else:
                raise Exception("this should never happen")

        ## if there is no intersection return None
        if len(values) == 0:
            return None

        ## uses the optional metadata from self but the individual metadata from other. Is this right??
        intersection_as_dict = {
            u"type": VALUE_TYPE_SET_STRING,
            u"name": self.name if self.name is not None else other.name,
            u"description": self.description if self.description is not None else other.description,
            VALUES_KEY_NAME: values,
        }

        return self.__class__(intersection_as_dict)
    

# class OptionObjectSieveValue(OptionSieveValue):
#     """
#     an object value
#
#     """
#     type = VALUE_TYPE_SET_OBJECT
#
#
#     def validate_single_value(self, value):
#         if not isinstance(value, dict):
#             raise Exception("should be dict %s" % value)
#
#
#     def _set_value_list(self, value_list):
#         self.value_list = value_list
#         for v in value_list:
#             self.validate_single_value(v)
#
#     def __str__(self):
#         return [v[u"value"] for v in self.value_list]
#
#
#     def isdisjoint(self, other):
#         """
#         This is an inefficient way to do this check as it has to iterate over both value lists and compare the results
#         possibly this could be improved
#         """
#         self.check_class(other)
#         for this_v in self.value_list:
#             for that_v in other.value_list:
#                 if this_v[u"value"] == that_v[u"value"]:
#                     return False
#         return True
#
#
#     def issubset(self, other):
#         """
#         methodology this time:
#         False if any or my values are not found in other
#         """
#         from winnow.options import OptionsSet
#         self.check_class(other)
#
#         for this_v in self.value_list:
#             found_v = False
#             for that_v in other.value_list:
#                 this_value_dict = this_v[u"value"]
#                 that_value_dict = that_v[u"value"]
#                 if this_value_dict == that_value_dict:
#                     this_options = this_value_dict.get(u"options")
#                     that_options = that_value_dict.get(u"options")
#                     if this_options is not None and that_options is not None:
#                         if not OptionsSet(that_options).allows(OptionsSet(this_options)):
#                             return False
#                     found_v = True
#             if not found_v:
#                 return False
#         return True


# class OptionFinishSieveValue(OptionSieveValue):
#
#     pass
#
#
# class OptionMaterialSieveValue(OptionSieveValue):
#
#     pass