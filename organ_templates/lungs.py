from tinydb import Query

from organ_templates.organ import Organ

class Lungs(Organ):
    def __init__(self):
        super(Lungs, self).__init__("lungs", "PulmonaryParameters")
        organ = Query()
        initvals = self._organ_parameters.search(organ.name == "lungs")