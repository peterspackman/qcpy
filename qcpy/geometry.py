"""
Geometry i.e. a set of atoms and their cartesian coordinates
"""
from collections import Counter
import logging
from typing import List
import numpy as np

from .atom import Atom
from .element import Element
from .formats.xyz import XYZFile
from .coordinates import Coordinates
from .utils import axis_rotation_matrix as rotation

Bohr = 0.5291772105638411

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
    comment = ""

    def __init__(self, atoms: List[Atom], *, charge: int = 0,
                 multiplicity: int = 1,
                 comment: str = ""):
        self.atoms = atoms
        self.charge = charge
        self.multiplicity = multiplicity
        self.comment = comment

    @staticmethod
    def from_xyz_file(filename, parse_comments=False):
        """Create a geometry from a given xyzfile"""
        xyz = XYZFile(filename, parse_comments)
        return Geometry(atoms=xyz.atoms,
                        charge=xyz.charge,
                        multiplicity=xyz.multiplicity,
                        comment=xyz.comment)

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
            # LOG.debug('Molecular formula: %s', self._molecular_formula)
        return self._molecular_formula

    def as_lines(self, *, line_format: str = "g09") -> str:
        """Return this geometry in a line by line string"""
        if line_format in _DEFAULT_FMT_STRING.keys():
            format_string = _DEFAULT_FMT_STRING[line_format]
        return [format_string.format(element=a.element,
                                     center=a.center) for a in self.atoms]


    def as_atomic_numbers(self):
        return np.array([atom.element.atomic_number for atom in self.atoms], dtype=int)

    def as_coordinate_matrix(self, *, units='angstrom'):
        m = np.array([atom.center.array for atom in self.atoms]).reshape((len(self.atoms), 3))
        if units == 'bohr':
            return m / Bohr
        return m

    def as_coordinate_array(self):
        return np.array([atom.center.array for atom in self.atoms])


    def rotate(self, *, x=0, y=0, z=0):
        mat = self.as_coordinate_matrix()
        rot = rotation(angle=x, axis='x').dot(
                rotation(angle=y, axis='y').dot(
                    rotation(angle=z, axis='z')))
        mat = mat.dot(rot)
        for i, row in enumerate(mat):
            self.atoms[i]._center = Coordinates(row)

    def move(self, vec):
        for atom in self.atoms:
            atom._center = Coordinates(atom.center.array + vec)

    def rescale(self, scale=Bohr):
        for atom in self.atoms:
            atom._center = Coordinates(atom.center.array * scale)

    @property
    def centroid(self):
        centers = np.array([atom.center.array for atom in self.atoms])
        return centers.mean(axis=0)

    @property
    def mean_radius(self):
        mat = self.as_coordinate_matrix()
        mat -= self.centroid
        return np.linalg.norm(mat, axis=1).mean()

    @property
    def bounding_sphere_radius(self):
        mat = self.as_coordinate_matrix()
        mat -= self.centroid
        return np.linalg.norm(mat, axis=1).max()

    def reoriginate(self):
        self.move(-self.centroid)

    def principle_axes(self):
        """Returns the eigenvectors of the
        coordinate matrix in descending order"""
        mat = self.as_coordinate_matrix()
        mat -= self.centroid
        cov = np.cov(mat.transpose())
        eigvals, eigvecs = np.linalg.eig(cov)
        idx = np.argsort(eigvals)[::-1]
        return eigvecs[:, idx]

    def principle_plane_normal(self):
        ax1, ax2, _ = self.principle_axes()
        return np.cross(ax1, ax2)

    @property
    def n_atoms(self) -> int:
        """The number of atoms in this geometry"""
        return len(self.atoms)

    def __str__(self) -> str:
        return self.molecular_formula

    def __repr__(self) -> str:
        return 'Geometry({self})'.format(self=self)
