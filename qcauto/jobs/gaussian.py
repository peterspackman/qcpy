import os
import logging
import attr
import re
from attr.validators import instance_of
from qcauto import Geometry
from qcauto.templates import GaussianSinglePointEnergy
log = logging.getLogger(__name__)


@attr.s
class GaussianJob(object):
    geometry = attr.ib(validator=instance_of(Geometry))
    _runner = attr.ib()
    basis_set = attr.ib(default="3-21G")
    method = attr.ib(default="HF")
    name = attr.ib(default='gaussian_job', validator=instance_of(str))
    template = attr.ib(default=GaussianSinglePointEnergy)

    def write_input_file(self, filename):
        log.debug("Writing input file to {}".format(filename))
        with open(filename, 'w') as f:
            f.write(self.template.render(job=self, geom=self.geometry))

    def run(self):
        log.debug("Running job {}".format(self.name))
        self._runner.run()
        return self._runner.result()

    def extract_energy(self, filename):
        log.debug("Extracting SCF energy from {}".format(filename))
        with open(filename) as f:
            for line in f:
                if 'SCF Done' in line:
                    return float(re.findall('[-+]\d+[\.]?\d*', line)[0])
