"""
All gaussian (g09) job classes
"""
import logging
from ..templates import GaussianSCF as SCF
from ..formats.gaussian import G09LogFile
from .job import GeometryJob, InputFileJob
import os

LOG = logging.getLogger(__name__)

D3BJ = 'EmpiricalDispersion=GD3BJ'



class UnknownmethodError(Exception):
    pass


class G09method:
    """Simple class representing a method available through
    g09"""
    def __init__(self, method, additional_keywords='', category='',
                 redundancy=None, correction=None, includes_dispersion=False):
        self.method = method
        self.additional = additional_keywords
        self.category = category
        self.redundancy = redundancy
        self.correction = correction
        self.includes_dispersion = includes_dispersion

    def __repr__(self):
        return 'g09: #p {} {}'.format(self.method, self.additional)

exchange_functionals = [
    's', 'xa', 'b', 'pw91', 'mpw', 'g96', 'pbe', 'o', 'tpss',
    'brx', 'pkzb', 'wpbeh', 'pbeh'
]

correlation_functionals = [
   'vwn', 'vwn5', 'lyp', 'pl', 'p86', 'pw91', 'b95', 'pbe',
   'tpss', 'kcis', 'brc', 'pkzb', 'vp86', 'v5lyp'
]

pure_functionals = [
    'vsxc', 'hcth', 'hcth93', 'hcth147', 'hcth407', 'thcth', 'mo6l',
    'b97', 'b97d', 'b97d3', 'sogga11', 'm11l', 'n12', 'mn12l', 'mn15l',
    'm06l'
]

hybrids = [
    'b3lyp', 'b3p86', 'b3pw91', 'b1b95', 'mpw1pw91', 'mpw1lyp',
    'mpw1pbe', 'mpw3pbe', 'b98', 'b971', 'b972', 'pbe1pbe', 'b1lyp',
    'o3lyp', 'bhandh', 'bhandhlyp', 'bmk', 'm06', 'm05', 'm052x',
    'm06hf', 'm062x', 'm08hx', 'mn15', 'pw6b95',
    'thcthhyb', 'apfd', 'apf', 'sogga11x', 'pbeh1pbe', 'tpssh', 'x3lyp'
]

rs_hybrids = [
    'hseh1pbe', 'ohse2pbe', 'ohse1pbe', 'wb97xd', 'wb97', 'wb97x',
    'lc-wpbe', 'cam-b3lyp', 'bissbpbe', 'm11', 'n12sx', 'mn12sx', 'lc-blyp',
    'lc-bp86', 'lc-bpw91', 'lc-pbepbe', 'lc-whpbe'
]

double_hybrids = [
    'mpw2plyp', 'dsdpbep86', 'pbe0dh', 'pbeq1dh'
]

available_methods = {
    'b2gpplyp': G09method('b2plyp', 'iop(3/125=0360003600,3/78=0640006400,'
                                      '3/76=0350006500,3/77=1000010000,5/33=1,3/124=-040)'),
    'b2kplyp': G09method('b2plyp',
                           'iop(3/125=0420004200,3/76=0280007200,'
                           '3/78=0580005800,3/77=1000010000,5/33=1)'),
    'b2tplyp': G09method('b2plyp', 
                           'iop(3/125=0310003100,3/76=0400006000,'
                           '3/78=0690006900,3/77=1000010000,5/33=1)'),
    'dsd-blyp': G09method('b2plyp',
                            'iop(3/125=0400004600,3/76=0300007000,'
                            '3/78=0560005600,3/77=1000010000,5/33=1)'),
    'dsd-pbep86': G09method('b2plyp',
                              'iop(3/125=0250005300,3/76=0300007000,'
                              '3/78=0430004300,3/74=1004,5/33=1)'),
    'hf': G09method('hf'),
    'mp2': G09method('mp2', includes_dispersion=True),
    'mpw1b95': G09method('mpwb95', 'iop(3/76=0690003100)'),
    'mpwb1k': G09method('mpwb95', 'iop(3/76=0560004400)'),
    'pbe38': G09method('pbepbe', 'iop(3/76=06250003750)'), # check this
    'pbesol': G09method('pbepbe', 'iop(3/74=5050)'), #
    'scs-mp2': G09method('mp2', redundancy='mp2', includes_dispersion=True,
                           correction={'a': 1.200, 'b': 0.333}),
    'sos-mp2': G09method('mp2', redundancy='mp2', includes_dispersion=True,
                           correction={'a': 1.300, 'b': 0.000}),
    'scs(mi)-mp2': G09method('mp2', redundancy='mp2', includes_dispersion=True,
                               correction={'a': 0.400, 'b': 1.290}),
    'scsn-mp2': G09method('mp2', redundancy='mp2', includes_dispersion=True,
                            correction={'a': 0.000, 'b': 1.760}),
    'scs-mp2-vdw': G09method('mp2', redundancy='mp2', includes_dispersion=True,
                               correction={'a': 1.280, 'b': 0.500}),
    's2-mp': G09method('mp2', redundancy='mp2', includes_dispersion=True,
                         correction={'a': 1.150, 'b': 0.750}),
}

for x in exchange_functionals:
    for c in correlation_functionals:
        available_methods[x+c] = G09method(x+c)

for xc in pure_functionals + hybrids + rs_hybrids + double_hybrids:
    available_methods[xc] = G09method(xc)

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
        'sto-3g', '3-21g', '6-21g', '4-31g', '6-31g',
        '6-311g', 'd95v', 'd95', 'shc', 'sec', 'cep-4g',
        'cep-31g', 'cep-121g', 'lanl2mp', 'lanl2dz', 'sdd',
        'sddall', 'cc-pvdz', 'cc-pvtz', 'cc-pvqz', 'cc-pv5z',
        'cc-pv6z', 'sv', 'svp', 'tzv', 'tzvp', 'def2sv', 'def2svp', 
        'def2svpp', 'def2tzvp', 'deftzvpp', 'def2qzv', 'def2qzvp',
        'def2qzvpp', 'qzvp', 'midix', 'epr-ii', 'epr-iii', 'ugbs',
        'dgdzvp', 'dgdzvp2', 'dgtzvp', 'cbsb7'
    ]

    _input_ext = '.gjf'
    _output_ext = '.log'
    _has_dependencies = True
    _requires_postprocessing = True
    _command = 'echo'
    _input_file = 'input.gjf'

    def __init__(self, **kwargs):
        self.params.update(kwargs)
        method = self.params['method'].lower()

        if not method in available_methods:
            raise(UnknownmethodError(self.params['method']))
        else:
            self.params['method'] = available_methods[method]

        if not 'geometry' in self.params:
            raise Exception('GaussianJob requires a geometry')

    def write_input_file(self, filename):
        LOG.debug("Writing input file to %s", filename)
        with open(filename, 'w') as input_file:
            input_file.write(self.render())

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
        if self.params['kind'] == 'scf':
            e = G09LogFile(self._output_file).scf_energy
            log.info('Energy (%s) = %g', self.params['name'], e)
        else:
            raise NotImplementedError

    def post_process(self):
        raise NotImplementedError

    def render(self):
        return self.params['template'].render(**self.params)

    @property
    def basis_set(self):
        return self.params['basis_set']

    def set_basis_set(self, basis_set):
        self.params['basis_set'] = basis_set 

    @property
    def method(self):
        return self.params['method']
