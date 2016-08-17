from unittest import TestCase
from qcauto.geometry import Geometry

class TestGeometry(TestCase):
    geom = Geometry.from_xyz_file('/tmp/h2o.xyz')

    def test_symbols(self):
        assert self.geom.atoms[0].element.name == 'oxygen'
        assert self.geom.atoms[1].element.name == 'hydrogen'
        assert self.geom.atoms[2].element.name == 'hydrogen'
    
    def test_as_lines(self):
        pass
