import logging
from qcauto.templates import GaussianSinglePointEnergy, GaussianWaveFunction
from .job import GeometryJob, InputFileJob
log = logging.getLogger(__name__)


class GaussianJob(GeometryJob, InputFileJob):
    _basis_set = "3-21G"
    _method = "HF"
    _name = "gaussian_job"
    _input_ext = '.gjf'
    _output_ext = '.log'

    def __init__(self, geometry, basis_set="3-21G", method="HF"):
        self._geometry = geometry
        self._method = method
        self._basis_set = basis_set 


    def write_input_file(self, filename):
        log.debug("Writing input file to {}".format(filename))
        with open(filename, 'w') as f:
            f.write(self._template.render(job=self, geom=self.geometry()))

    def before_run(self):
        log.debug("before_run in {}".format(self.__class__.__name__))
        file_basename = self._name + self._method + self._basis_set
        self._input_file = file_basename + self._input_ext
        self._output_file = file_basename + self._output_ext
        self.write_input_file(self._input_file)

    def read_output_file(self, filename):
        pass

    def after_run(self):
        pass

    def result(self):
        pass

    def args(self):
        return [self._input_file]


class GaussianWaveFunctionJob(GaussianJob):
    _template = GaussianWaveFunction
    fchk_name = "wavefunction"


class GaussianSinglePointEnergyJob(GaussianJob):
    _template = GaussianSinglePointEnergy

