from tinydb import Query

from Organ_templates.organ import Organ

class Lungs(Organ):
    def __init__(self):
        super(Lungs, self).__init__("lungs")
        organ = Query()
        initvals = self._organ_parameters.search(organ.name == "lungs")
        print(initvals)