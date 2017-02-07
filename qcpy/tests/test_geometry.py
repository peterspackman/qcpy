"""
Geometry tests
"""
from unittest import TestCase
from qcpy.element import O, H
from qcpy.atom import Atom
from qcpy.coordinates import Coordinates
from qcpy.geometry import Geometry

H2O = Geometry(atoms=[
    Atom(O, center=Coordinates(0.0, 0.0, 0.11779)),
    Atom(H, center=Coordinates(0.0, 0.7554530, -0.471161)),
    Atom(H, center=Coordinates(0.0, -0.7554530, -0.471161))],
               charge=0, multiplicity=1)


class TestGeometry(TestCase):
    """Test case for Geometry object"""
    geom = H2O

    def test_elements(self):
        """Geometry elements"""
        self.assertEqual(self.geom.elements, [O, H, H])

    def test_molecular_formula(self):
        """Calculated molecular formula"""
        self.assertEqual(self.geom.molecular_formula, "H2O")

    def test_as_lines(self):
        """Render geometry as text lines"""
        self.assertEqual(self.geom.as_lines(),
                        ["O    0.0000000   0.0000000   0.1177900",
                         "H    0.0000000   0.7554530  -0.4711610",
                         "H    0.0000000  -0.7554530  -0.4711610"])
