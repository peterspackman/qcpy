import attr
from attr.validators import instance_of
from qcauto.formats.xyz import XYZFile

@attr.s
class Geometry:
    atoms = attr.ib(default=attr.Factory(list))
    charge = attr.ib(default=0, validator=instance_of(int))
    multiplicity = attr.ib(default=1, validator=instance_of(int))

    @staticmethod
    def from_xyz_file(filename):
        return Geometry(atoms=XYZFile(filename).atoms, charge=0, multiplicity=1)

    def as_lines(self, format_string="{symbol:<2}  {x: 09.7f}  {y: 09.7f}  {z: 09.7f}"):
        return [format_string.format(symbol=atom.element.symbol,
                                     x=atom.center.x,
                                     y=atom.center.y,
                                     z=atom.center.z) for atom in self.atoms]
