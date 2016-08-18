import attr
from attr.validators import instance_of


@attr.s
class Coordinates:
    x = attr.ib(validator=instance_of(float))
    y = attr.ib(validator=instance_of(float))
    z = attr.ib(validator=instance_of(float))
    units = attr.ib(default="angstroms")
