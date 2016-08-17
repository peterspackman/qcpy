import attr
from attr.validators import instance_of
from periodictable.core import Element

@attr.s
class Coordinates:
    x = attr.ib(validator=instance_of(float))
    y = attr.ib(validator=instance_of(float))
    z = attr.ib(validator=instance_of(float))
    units = attr.ib(default="angstroms")

@attr.s
class Atom:
    element = attr.ib(validator=instance_of(Element))
    center = attr.ib(validator=instance_of(Coordinates))
