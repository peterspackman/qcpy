"""
Geometry tests
"""
from unittest import TestCase
from qcauto.element import O, H
from qcauto.atom import Atom
from qcauto.coordinates import Coordinates
from qcauto.geometry import Geometry

H2O = Geometry(atoms=[
    Atom(O, center=Coordinates(0.0, 0.0, 0.11779)),
    Atom(H, center=Coordinates(0.0, 0.7554530, -0.471161)),
    Atom(H, center=Coordinates(0.0, -0.7554530, -0.471161))],
               charge=0, multiplicity=1)


class TestGeometry(TestCase):
    """Test case for Geometry object"""
    geom = H2O

    def test_elements(self):
        """Check that the elements are correct"""
        assert self.geom.elements == [O, H, H]

    def test_molecular_formula(self):
        """Check that the calculated molecular formula is correct"""
        assert self.geom.molecular_formula == "H2O"

    def test_as_lines(self):
        """Check output as lines"""
        assert self.geom.as_lines() == ["O    0.0000000   0.0000000   0.1177900",
                                        "H    0.0000000   0.7554530  -0.4711610",
                                        "H    0.0000000  -0.7554530  -0.4711610"]
