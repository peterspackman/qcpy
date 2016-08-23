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
    _has_dependencies = True
    _requires_postprocessing = True

    def __init__(self, geometry, basis_set="3-21G", method="HF"):
        self._geometry = geometry
        self._method = method
        self._basis_set = basis_set

    def write_input_file(self, filename):
        log.debug("Writing input file to {}".format(filename))
        with open(filename, 'w') as f:
            f.write(self.render(job=self, geom=self.geometry()))

    @property
    def default_basename(self):
        return self._name + self._method + self._basis_set

    def resolve_dependencies(self):
        log.debug("Resolving dependences for {}".format(self.name))

        self._input_file = self.default_basename + self._input_ext
        self._output_file = self.default_basename + self._output_ext
        self.write_input_file(self._input_file)

    def read_output_file(self, filename):
        pass


class GaussianWaveFunctionJob(GaussianJob):
    _template = GaussianWaveFunction
    _fchk_filename = "wavefunction"

    @property
    def fchk_filename(self):
        return self._fchk_filename

    def set_fchk_filename(self, filename):
        self._fchk_filename = filename


class GaussianSinglePointEnergyJob(GaussianJob):
    _template = GaussianSinglePointEnergy

