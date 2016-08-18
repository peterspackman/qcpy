import logging
import attr
from attr.validators import instance_of
from qcauto.formats.xyz import XYZFile
from collections import Counter
log = logging.getLogger(__name__)

_specs = {
    "g09": "{element.symbol:<2}  "
           "{center.x: 09.7f}  "
           "{center.y: 09.7f}  "
           "{center.z: 09.7f}",
    "tonto": "{element.symbol:<2}"
             "{center.x: 09.7f}  "
             "{center.y: 09.7f}  "
             "{center.z: 09.7f}",
}


@attr.s
class Geometry:
    atoms = attr.ib(default=attr.Factory(list))
    charge = attr.ib(default=0, validator=instance_of(int))
    multiplicity = attr.ib(default=1, validator=instance_of(int))

    @staticmethod
    def from_xyz_file(filename):
        return Geometry(atoms=XYZFile(filename).atoms,
                        charge=0, multiplicity=1)

    def elements(self):
        return [a.element for a in self.atoms]

    def molecular_formula(self):
        f_string = ""
        symbols = map(lambda x: x.symbol, self.elements())
        for symbol, count in sorted(Counter(symbols).items(),
                                    key=lambda c: c[0]):
            f_string += symbol + (str(count) if count > 1 else "")
        log.debug('formula = {}'.format(f_string))
        return f_string

    def as_lines(self, format="g09"):
        if format in _specs.keys():
            format_string = _specs[format]
        return [format_string.format(element=a.element,
                                     center=a.center) for a in self.atoms]
