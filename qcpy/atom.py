"""
Store all the desired info about an atom in a molecule etc
"""
from .element import periodictable
from .coordinates import Coordinates


class Atom:
    """An atom consists of a position in 3D space, and an element type
    >>> a = Atom.from_symbol_and_location('H', [0, 0, 0])
    >>> a
    H: [0, 0, 0]
    >>> a.covalent_radius
    0.23
    """
    _element = None
    _center = None

    def __init__(self, element, center):
        self._element = element
        self._center = Coordinates(center)

    @staticmethod
    def from_symbol_and_location(symbol, center):
        """ Create a new Atom from a given atomic symbol and coordinates
        """
        return Atom(periodictable[symbol], center=center)

    @staticmethod
    def from_number_and_location(number, center):
        """ Create a new Atom from a given atomic symbol and coordinates
        """
        return Atom(periodictable[number], center=center)


    @property
    def element(self):
        """Return the element object associated with this atom"""
        return self._element

    @property
    def center(self):
        """Return the center of the atom in cartesian coordinates"""
        return self._center

    @property
    def covalent_radius(self):
        """This atom's covalent radius in angstroms"""
        return self.element.covalent_radius

    def __str__(self):
        return "{}: {}".format(self.element, self.center)

    def __repr__(self):
        return str(self)
