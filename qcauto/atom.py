import attr
from .coordinates import Coordinates
from attr.validators import instance_of
from periodictable.core import Element


@attr.s
class Atom:
    element = attr.ib(validator=instance_of(Element))
    center = attr.ib(validator=instance_of(Coordinates))
