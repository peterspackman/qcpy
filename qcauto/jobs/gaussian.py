import os
import logging
import attr
from attr.validators import instance_of
from qcauto.geometry import Geometry
from qcauto.templates import GaussianSinglePointEnergy
from qcauto.jobs.runners import LocalRunner
log = logging.getLogger(__name__)

@attr.s
class GaussianJob(object):
    geometry = attr.ib(validator=instance_of(Geometry))
    basis_set = attr.ib(default="3-21G")
    method = attr.ib(default="HF")
    name = attr.ib(default='gaussian_job', validator=instance_of(str))
    template = attr.ib(default=GaussianSinglePointEnergy)
    _runner = attr.ib(default=LocalRunner(executable_path='/Users/prs/bin/g09/g09'))

    def write_input_file(self, filename):
        with open(filename, 'w') as f:
            f.write(self.template.render(job=self, geom=self.geometry))

    def run():
        _runner.run()

    def extract_gjf_energy(filename):
        with open(filename) as f:
            for line in f:
                if 'SCF Done' in line:
                    return float(re.findall('[-+]\d+[\.]?\d*', line)[0])

