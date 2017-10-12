from tinydb import Query
from organ_templates.organ import Organ

class Other(Organ):
    def __init__(self):
        super(Other, self).__init__("other", "SystemicParameters")
        organ = Query()
        initvals = self._organ_parameters.search(organ.name == "other")
