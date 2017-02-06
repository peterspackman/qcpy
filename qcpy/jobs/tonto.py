"""All tonto job classes"""
import logging
from ..templates import TontoRobyBondIndex as Roby
from ..templates import TontoSCF as SCF
from .job import GeometryJob, InputFileJob
LOG = logging.getLogger(__name__)

def kwdict_to_string(d, prefix=''): 
    lines = []
    for key, value in d.items():
        if value is None:
            lines.append('{}{}'.format(prefix, key))
        else:
            if isinstance(value, dict):
                lines.append('{}{}= {{'.format(prefix, key))
                lines.append(kwdict_to_string(value, prefix=prefix+'  '))
                lines.append('{}}}'.format(prefix))
            else:
                lines.append('{}{}= {}'.format(prefix, key, value))
    return '\n'.join(lines)


class TontoJob(GeometryJob, InputFileJob):
    """ Abstract base class for tonto jobs"""
    _basis_set = "3-21G"
    _method = "RHF"
    _name = "tonto_job"
    _has_dependencies = True
    _requires_postprocessing = True
    _basis_directory = None
    _template = SCF

    _scf_keywords = {
        'scfdata': {
            'initial_density': 'promolecule',
            'kind': 'rhf',
            'direct': 'on',
            'convergence': 0.00001,
            'diis': { 'convergence_tolerance': 0.00001},
            'output': 'NO',
            'output_results': 'YES'
        },
        'scf': None,
        'delete_scf_archives': None,
    }

    _output_keywords = {}

    def __init__(self, geometry, basis_set="3-21G", method="HF", command='tonto'):
        self._geometry = geometry
        self._method = method
        self._basis_set_name = basis_set
        self._command = command


    def write_input_file(self, filename: str):
        LOG.debug("Writing input file to %s", filename)
        with open(filename, 'w') as input_file:
            input_file.write(self._template.render(job=self))

    def resolve_dependencies(self):
        LOG.debug("Resolving dependencies for tonto job %s", self.name)
        self.write_input_file(self.input_filename)

    @property
    def charge(self):
        return self._charge

    @property
    def multiplicity(self):
        return self._multiplicity

    @property
    def basis_name(self):
        return self._basis_set_name

    def scf_block_string(self):
        return kwdict_to_string(self._scf_keywords)

    def output_block_string(self):
        return kwdict_to_string(self._output_keywords)

    def read_output_file(self, filename):
        pass

    def post_process(self):
        pass


class TontoRobyBondIndexJob(TontoJob):
    """Class to run roby bond index jobs"""
    _fchk_filename = "wavefunction.fchk"
    _template = Roby

    @property
    def fchk_filename(self) -> str:
        """Returns the fchk filename for this job"""
        return self._fchk_filename

    def resolve_dependencies(self):
        import os
        assert os.path.exists(self.fchk_filename)
        super().resolve_dependencies()
