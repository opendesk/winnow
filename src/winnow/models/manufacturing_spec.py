import winnow
from winnow.models.base import WinnowVersion



class WinnowManufacturingSpecfifcation(WinnowVersion):

    @property
    def id(self):
        return self.kwargs[u"uuid"]