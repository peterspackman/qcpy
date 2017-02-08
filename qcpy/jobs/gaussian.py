"""
All gaussian (g09) job classes
"""
import logging
from ..templates import GaussianSCF as SCF
from ..formats.gaussian import G09LogFile
from .job import GeometryJob, InputFileJob

LOG = logging.getLogger(__name__)


class GaussianJob(GeometryJob, InputFileJob):
    """Base class for all g09 jobs"""
    params = {
        'kind': 'scf',
        'basis_set': '6-31G',
        'method': 'hf',
        'name': 'g09_job',
        'template': SCF,
        'basis directory': None,
    }

    _available_basis_sets = [
       '3-21G', '6-311++G(2d,2p)', '6-311G(d,p)',
       '6-31G(d)', '6-31G(d,p)', 'Clementi-Roetti',
       'Coppens', 'DZP', 'DZP-DKH', 'STO-3G', 'Sadlej+',
       'Sadlej-PVTZ', 'Spackman-DZP+', 'TZP-DKH', 'Thakkar',
       'VTZ-Ahlrichs', 'ahlrichs-polarization', 'aug-cc-pVDZ',
       'aug-cc-pVQZ', 'aug-cc-pVTZ', 'cc-pVDZ', 'cc-pVQZ',
       'cc-pVTZ', 'def2-SV(P)', 'def2-SVP', 'def2-TZVP',
       'def2-TZVPP', 'pVDZ-Ahlrichs', 'vanLenthe-Baerends'
    ]

    _input_ext = '.gjf'
    _output_ext = '.log'
    _has_dependencies = True
    _requires_postprocessing = True
    _command = 'echo'
    _input_file = 'input.gjf'

    def __init__(self, **kwargs):
        self.params.update(kwargs)

    def write_input_file(self, filename):
        LOG.debug("Writing input file to %s", filename)
        with open(filename, 'w') as input_file:
            input_file.write(self.render(params=self.params))

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
