"""All tonto job classes"""
import logging
from ..templates import TontoSCF as SCF
from ..formats.tonto_output import TontoOutputFile
from .job import GeometryJob, InputFileJob, InvalidBasisSetName
LOG = logging.getLogger(__name__)


class TontoKeywords(dict):
    def as_input_lines(d, prefix=''): 
        lines = []
        for key, value in d.items():
            if value is None:
                lines.append('{}{}'.format(prefix, key))
            else:
                if isinstance(value, dict):
                    lines.append('{}{}= {{'.format(prefix, key))
                    lines.append(TontoKeywords(value).as_input_lines(prefix=prefix+'  '))
                    lines.append('{}}}'.format(prefix))
                else:
                    lines.append('{}{}= {}'.format(prefix, key, value))
        return '\n'.join(lines)


class TontoJob(GeometryJob, InputFileJob):
    """Abstract base class for tonto jobs"""
    _has_dependencies = True
    _requires_postprocessing = True
    _input_filename = 'stdin'
    _output_filename = 'stdout'

    params = {
        'kind': 'scf',
        'basis_set': '3-21G',
        'method': 'hf',
        'name': 'tonto_job',
        'template': SCF,
        'basis directory': None,
        'scf_keywords': TontoKeywords({
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
        }),
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

    def __init__(self, **kwargs):
        self.params.update(kwargs)

    def write_input_file(self, filename: str):
        LOG.debug("Writing input file to %s", filename)
        with open(filename, 'w') as input_file:
            input_file.write(self.render())

    def resolve_dependencies(self):
        LOG.debug("Resolving dependencies for tonto job %s", self.name)
        self.write_input_file(self.input_filename)

    @property
    def basis_set(self):
        return self.params['basis_set']

    def set_basis_set(self, basis_set):
        if not basis_set in self.available_basis_sets:
            raise InvalidBasisSetName(
                    "No such basis in tonto: {}".format(basis_set))
        self.params['basis_set'] = basis_set

    def render(self):
        LOG.debug("Rendering template %s", self.params['template'])
        return self.params['template'].render(**self.params)

    @property
    def available_basis_sets(self):
        return self._available_basis_sets

    def read_output_file(self, filename):
        of = TontoOutputFile(filename)
        return of.structured_contents

    def post_process(self):
        contents = self.read_output_file(self._output_file)
        return contents
