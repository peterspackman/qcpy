"""All tonto job classes"""
import logging
from ..templates import TontoRobyBondIndex as Roby
from ..templates import TontoSCF as SCF
from ..formats.tonto_output import TontoOutputFile
from .job import GeometryJob, InputFileJob, InvalidBasisSetName
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
    """Abstract base class for tonto jobs"""
    _basis_set = "3-21G"
    _method = "RHF"
    _name = "tonto_job"
    _has_dependencies = True
    _requires_postprocessing = True
    _basis_directory = None
    _template = SCF
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
        self._basis_set = basis_set
        self._command = command


    def write_input_file(self, filename: str):
        LOG.debug("Writing input file to %s", filename)
        with open(filename, 'w') as input_file:
            input_file.write(self._template.render(job=self))

    def resolve_dependencies(self):
        LOG.debug("Resolving dependencies for tonto job %s", self.name)
        self.write_input_file(self.input_filename)

    @property
    def basis_set(self):
        return self._basis_set

    def set_basis_set(self, basis_set):
        if not basis_set in self.available_basis_sets:
            raise InvalidBasisSetName(
                    "No such basis in tonto: {}".format(basis_set))
        self._basis_set = basis_set

    @property
    def available_basis_sets(self):
        return self._available_basis_sets

    def scf_block_string(self):
        return kwdict_to_string(self._scf_keywords)

    def output_block_string(self):
        return kwdict_to_string(self._output_keywords)

    def read_output_file(self, filename):
        of = TontoOutputFile(filename)
        return of.structured_contents

    def post_process(self):
        pass


class TontoRobyBondIndexJob(TontoJob):
    """Class to run roby bond index jobs"""
    _fchk_filename = "wavefunction.fchk"
    _template = Roby

    @property
    def fchk_filename(self) -> str:
        """Returns the fchk filename for this job

        >>> from qcpy.tests.test_geometry import H2O
        >>> job = TontoRobyBondIndexJob(H2O)
        >>> job.fchk_filename
        'wavefunction.fchk'
        """
        return self._fchk_filename

    def set_fchck_filename(self, filename):
        """Sets the fchk filename for this job"""
        self._fchk_filename = filename

    def resolve_dependencies(self):
        import os
        assert os.path.exists(self.fchk_filename)
        super().resolve_dependencies()
