
from winnow.exceptions import OptionsExceptionFailedValidation
from winnow.utils import json_dumps


class BaseWinnowValue(object):

    def __init__(self, value):

        if isinstance(value, dict):
            self.name = value.get("name")
            self.description = value.get("description")
            self.image_url = value.get("image_url")
            self.scopes = value.get("scopes")
        else:
            self.name = None
            self.description = None
            self.image_url = None
            self.scopes = None


    def get_merged_info(self, other):

        return {
            u"scopes": self.scopes if self.scopes is not None else other.scopes,
            u"image_url": self.image_url if self.image_url is not None else other.image_url,
            u"name": self.name if self.name is not None else other.name,
            u"description": self.description if self.description is not None else other.description,
        }

    def check_class(self, other):
        return
        if not self.__class__ == other.__class__:
            raise Exception("sieve value types must match")

    def __str__(self):
        return json_dumps(self.as_json())


    def update_with_info(self, as_json):

        if self.name is not None:
            as_json[u"name"] = self.name
        if self.description is not None:
            as_json[u"description"] = self.description
        if self.image_url is not None:
            as_json[u"image_url"] = self.image_url
        if self.scopes is not None:
            as_json[u"scopes"] = self.scopes

        return as_json













