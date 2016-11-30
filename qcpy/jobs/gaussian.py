"""
All gaussian (g09) job classes
"""
import logging
from ..templates import GaussianSinglePointEnergy, GaussianWaveFunction
from ..formats.gaussian import G09LogFile
from .job import GeometryJob, InputFileJob

LOG = logging.getLogger(__name__)


class GaussianJob(GeometryJob, InputFileJob):
    """Base class for all g09 jobs"""
    _basis_set_name = "3-21G"
    _method = "HF"
    _name = "gaussian_job"
    _input_ext = '.gjf'
    _output_ext = '.log'
    _has_dependencies = True
    _requires_postprocessing = True
    _command = 'echo'
    _input_file = 'input.gjf'

    def __init__(self, geometry, basis_set="3-21G", method="HF", command='g09'):
        self._geometry = geometry
        self._method = method
        self._basis_set_name = basis_set
        self._command = command

    def write_input_file(self, filename):
        LOG.debug("Writing input file to %s", filename)
        with open(filename, 'w') as input_file:
            input_file.write(self.render(job=self, geom=self.geometry()))

    @property
    def command(self):
        """What is the current 'command' e.g. /bin/g09"""
        return [self._command, self._input_file]

    @property
    def default_basename(self):
        """Get the default basename for this job e.g. h2o_b3lyp_sto3g"""
        return "{}_{}_{}".format(self._name, self._method, self._basis_set_name)

    def resolve_dependencies(self):
        LOG.debug("Resolving dependences for %s", self.name)
        self._input_file = self.default_basename + self._input_ext
        self._output_file = self.default_basename + self._output_ext
        self.write_input_file(self._input_file)

    def read_output_file(self, filename):
        pass

    def post_process(self):
        raise NotImplementedError

    @property
    def basis_set(self):
        return self._basis_set_name

    @property
    def method(self):
        return self._method


class GaussianWaveFunctionJob(GaussianJob):
    """Base class for all g09 wavefunction jobs"""
    _template = GaussianWaveFunction
    _fchk_filename = "wavefunction"

    @property
    def fchk_filename(self):
        """Return the filename of the output fchk file i.e. the wavefunction file"""
        return self._fchk_filename

    def set_fchk_filename(self, filename):
        """Set the wavefunction file name"""
        self._fchk_filename = filename

    def post_process(self):
        raise NotImplementedError


class GaussianSinglePointEnergyJob(GaussianJob):
    """Run a single point energy job using g09"""
    _template = GaussianSinglePointEnergy

    def post_process(self):
        log_file = G09LogFile(self.output_file)
        self._result = log_file.scf_energy

