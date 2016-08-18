import os
import logging
import attr
import re
from attr.validators import instance_of
from qcauto import Geometry
from qcauto.templates import GaussianSinglePointEnergy
from qcauto.jobs.runners import NullRunner
log = logging.getLogger(__name__)


@attr.s
class GaussianJob(object):
    geometry = attr.ib(validator=instance_of(Geometry))
    _runner = attr.ib(default=NullRunner())
    basis_set = attr.ib(default="3-21G")
    method = attr.ib(default="HF")
    name = attr.ib(default='gaussian_job', validator=instance_of(str))
    input_ext = attr.ib('.gjf')
    output_ext = attr.ib('.log')
    template = attr.ib(default=GaussianSinglePointEnergy)

    def write_input_file(self, filename):
        log.debug("Writing input file to {}".format(filename))
        with open(filename, 'w') as f:
            f.write(self.template.render(job=self, geom=self.geometry))

    def run(self):
        log.debug("Running job {}".format(self.name))

        if not isinstance(self._runner, NullRunner):
            file_basename = self.name + self.method + self.basis_set
            input_file = file_basename + self.input_ext

            self.write_input_file(input_file)
            self._runner.run(args=[input_file])
            if not self.successful():
                return None
            return self.extract_energy(file_basename + self.output_ext)
        else:
            return None

    def set_runner(self, runner):
        self._runner = runner

    def successful(self):
        return self._runner.successful()

    def extract_energy(self, filename):
        log.debug("Extracting SCF energy from {}".format(filename))
        with open(filename) as f:
            for line in f:
                if 'SCF Done' in line:
                    return float(re.findall('[-+]\d+[\.]?\d*', line)[0])
