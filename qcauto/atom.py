import attr
from qcauto.coordinates import Coordinates
from qcauto.element import Element, periodictable
from attr.validators import instance_of


@attr.s
class Atom:
    element = attr.ib(validator=instance_of(Element))
    center = attr.ib(validator=instance_of(Coordinates))

    @staticmethod
    def from_symbol_and_location(symbol, center):
        """ Create a new Atom from a given atomic symbol and coordinates
        >>> Atom.from_symbol_and_location('Ca', Coordinates(0, 0, 0))
        Atom(element=Ca, center=Coordinates(x=0.0, y=0.0, z=0.0))
        >>> Atom.from_symbol_and_location('Bo', Coordinates(1, 1, 0))
        Traceback (most recent call last):
         ...
        KeyError: "No such element 'Bo'"
        """
        return Atom(periodictable[symbol], center=center)
