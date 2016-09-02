import attr
from qcauto.coordinates import Coordinates
from attr.validators import instance_of
import periodictable


@attr.s
class Atom:
    element = attr.ib(validator=instance_of(periodictable.core.Element))
    center = attr.ib(validator=instance_of(Coordinates))

    @staticmethod
    def from_symbol_and_location(symbol, center):
        """ Create a new Atom from a given atomic symbol and coordinates
        >>> Atom.from_symbol_and_location('Ca', Coordinates(0, 0, 0))
        Atom(element=Ca, center=Coordinates(x=0.0, y=0.0, z=0.0))
        >>> Atom.from_symbol_and_location('Bo', Coordinates(1, 1, 0))
        Traceback (most recent call last):
         ...
        ValueError: unknown element Bo
        """
        return Atom(periodictable.elements.symbol(symbol), center=center)
