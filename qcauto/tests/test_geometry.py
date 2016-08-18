from unittest import TestCase
from periodictable import O, H
from qcauto.atom import Atom, Coordinates
from qcauto.geometry import Geometry

H2O = Geometry(atoms=[
    Atom(O,center=Coordinates(0.0, 0.0 ,0.11779)),
    Atom(H,center=Coordinates(0.0, 0.7554530, -0.471161)),
    Atom(H,center=Coordinates(0.0, -0.7554530, -0.471161))],
    charge=0, multiplicity=1)

class TestGeometry(TestCase):
    geom = H2O

    def test_elements(self):
        assert self.geom.elements() == [O, H, H]
    
    def test_molecular_formula(self):
        assert self.geom.molecular_formula() == "H2O"

    def test_as_lines(self):
        pass
