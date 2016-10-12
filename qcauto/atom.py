"""
Store all the desired info about an atom in a molecule etc
"""
from qcauto.element import periodictable


class Atom:
    """TODO Atom documentation"""
    _element = None
    _center = None
    
    def __init__(self, element, center):
        self._element = element
        self._center = center

    @staticmethod
    def from_symbol_and_location(symbol, center):
        """ Create a new Atom from a given atomic symbol and coordinates
        """
        return Atom(periodictable[symbol], center=center)

    @property
    def element(self):
        return self._element
    
    @property
    def center(self):
        return self._center
    
    @property
    def covalent_radius(self):
        """This atom's covalent radius in angstroms"""
        return self.element.covalent_radius
