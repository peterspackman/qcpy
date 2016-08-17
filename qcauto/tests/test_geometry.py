from unittest import TestCase
from periodictable import H
from qcauto.atom import Atom, Coordinates
from qcauto.geometry import Geometry

class TestGeometry(TestCase):
    geom = Geometry(atoms=[Atom(H,center=Coordinates(0.,0.,0.)),
                           Atom(H,center=Coordinates(0.,1.4,0.))],
                           charge=0, multiplicity=1)

    def test_symbols(self):
        assert self.geom.atoms[0].element.name == 'hydrogen'
        assert self.geom.atoms[1].element.name == 'hydrogen'
    
    def test_as_lines(self):
        pass
