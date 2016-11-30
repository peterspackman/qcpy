"""
Geometry i.e. a set of atoms and their cartesian coordinates
"""
from collections import Counter
import logging
from typing import List

from .atom import Atom
from .element import Element
from .formats.xyz import XYZFile

LOG = logging.getLogger(__name__)

_DEFAULT_FMT_STRING = {
    "g09": "{element.symbol:<2}  "
           "{center.x: 09.7f}  "
           "{center.y: 09.7f}  "
           "{center.z: 09.7f}",
    "tonto": "{element.symbol:<2}"
             "{center.x: 09.7f}  "
             "{center.y: 09.7f}  "
             "{center.z: 09.7f}",
}

class Geometry:
    """A group of atoms and their coordinates"""
    atoms = []
    charge = 0
    multiplicity = 1
    _molecular_formula = ""

    def __init__(self, atoms: List[Atom], charge: int = 0,
                 multiplicity: int = 1):
        self.atoms = atoms
        self.charge = charge
        self.multiplicity = multiplicity

    @staticmethod
    def from_xyz_file(filename):
        """Create a geometry from a given xyzfile"""
        return Geometry(atoms=XYZFile(filename).atoms,
                        charge=0, multiplicity=1)

    @property
    def elements(self) -> List[Element]:
        """Returns a list of the elements in this geometry"""
        return [a.element for a in self.atoms]

    @property
    def molecular_formula(self) -> str:
        """Returns the molecular formula of this geometry"""
        if not self._molecular_formula:
            symbols = [x.symbol for x in self.elements]
            for symbol, count in sorted(Counter(symbols).items(),
                                        key=lambda c: c[0]):
                self._molecular_formula += symbol + (str(count) if count > 1 else "")
            LOG.debug('Molecular formula: %s', self._molecular_formula)
        return self._molecular_formula

    def as_lines(self, line_format: str = "g09") -> str:
        """Return this geometry in a line by line string"""
        if line_format in _DEFAULT_FMT_STRING.keys():
            format_string = _DEFAULT_FMT_STRING[line_format]
        return [format_string.format(element=a.element,
                                     center=a.center) for a in self.atoms]

    @property
    def n_atoms(self) -> int:
        """The number of atoms in this geometry"""
        return len(self.atoms)
