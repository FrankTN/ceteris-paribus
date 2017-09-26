from tinydb import Query
from Organ_templates.organ import Organ


class Other(Organ):
    def __init__(self):
        super(Other, self).__init__("Other")
        organ = Query()
        initvals = self._organ_parameters.search(organ.name == "other")
        print(initvals)

Other()