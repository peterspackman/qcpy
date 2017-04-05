"""
All gaussian (g09) job classes
"""
import logging
from ..templates import GaussianSCF as SCF
from ..formats.gaussian import G09LogFile
from .job import GeometryJob, InputFileJob

LOG = logging.getLogger(__name__)

D3BJ = 'EmpiricalDispersion=GD3BJ'

class UnknownProtocolError(Exception):
    pass

class G09Protocol:
    """Simple class representing a method available through
    g09"""
    def __init__(self, method, additional_keywords='', category='',
                 redundancy=None):
        self.method = method
        self.additional = additional_keywords
        self.category = category
        self.redundancy = redundancy

    def __repr__(self):
        return '<G09: # {}/{{basis_set}} {}>'.format(self.method, self.additional)


available_protocols = {
    'b1b95': G09Protocol('B1B95'),
    'b1b95-d3bj': G09Protocol('B1B95', D3BJ),
    'b2gpplyp': G09Protocol('B2PLYP', 'iop(3/125=0360003600,3/78=0640006400,'
                                      '3/76=0350006500,3/77=1000010000,5/33=1,3/124=-040)'),
    'b2gpplyp-d3bj': G09Protocol('B2PLYP', 'iop(3/125=0360003600,3/78=0640006400,3/76=0350006500,'
                                           '3/77=1000010000,5/33=1,3/124=-040) ' + D3BJ),
    'b2plyp': G09Protocol('B2PLYP'),
    'b2plyp-d3bj': G09Protocol('B2PLYP', D3BJ),
    'b3lyp': G09Protocol('B3LYP'),
    'b3lyp-d3bj': G09Protocol('B3LYP', D3BJ),
    'b3pw91': G09Protocol('B3PW91'),
    'b3pw91-d3bj': G09Protocol('B3PW91', D3BJ),
    'b97': G09Protocol('B97'),
    'b97-d3bj': G09Protocol('B97', D3BJ),
    'bhlyp': G09Protocol('BHandHLYP'),
    'bhlyp-d3bj': G09Protocol('BHandHLYP', D3BJ),
    'blyp': G09Protocol('BLYP'),
    'blyp-d3bj': G09Protocol('BLYP', D3BJ),
    'bmk': G09Protocol('BMK'),
    'bmk-d3bj': G09Protocol('BMK', D3BJ),
    'bop': G09Protocol('BOP'),
    'bop-d3bj': G09Protocol('BOP', D3BJ), #
    'bp86': G09Protocol('BP86'),
    'bp86-d3bj': G09Protocol('BP86', D3BJ),
    'bpbe': G09Protocol('BPBE'),
    'bpbe-d3bj': G09Protocol('BPBE', D3BJ),
    'cam-b3lyp': G09Protocol('CAM-B3LYP'),
    'cam-b3lyp-d3bj': G09Protocol('CAM-B3LYP', D3BJ),
    'dsd-blyp': G09Protocol('DSD-BLYP'), #
    'dsd-blyp-d3bj': G09Protocol('DSD-BLYP', D3BJ),
    'hf': G09Protocol('HF'),
    'brh': G09Protocol('SVWN5','iop(3/76=0000010000)'), 
    'hf-d3bj': G09Protocol('HF', D3BJ),
    'lc-ωpbe': G09Protocol('LC-wPBE'),
    'lc-ωpbe-d3bj': G09Protocol('LC-wPBE', D3BJ),
    'm05': G09Protocol('M05'),
    'm05-d3bj': G09Protocol('M05', D3BJ),
    'm052x': G09Protocol('M052X'),
    'm052x-d3bj': G09Protocol('M052X', D3BJ),
    'm06': G09Protocol('M06'),
    'm06-d3bj': G09Protocol('M06', D3BJ),
    'm062x': G09Protocol('M062X'),
    'm062x-d3bj': G09Protocol('M062X', D3BJ),
    'm06hf': G09Protocol('M06HF'),
    'm06hf-d3bj': G09Protocol('M06HF', D3BJ),
    'm06l': G09Protocol('M06L'),
    'm06l-d3bj': G09Protocol('M06L', D3BJ),
    'mp2': G09Protocol('MP2'),
    'mpw1b95': G09Protocol('mPWB95', 'iop(3/76=0690003100)'),
    'mpw1b95-d3bj': G09Protocol('mPWB95', 'iop(3/76=0690003100) ' + D3BJ),
    'mpwb1k': G09Protocol('mPWB95', 'iop(3/76=0560004400)'),
    'mpwb1k-d3bj': G09Protocol('mPWB95', 'iop(3/76=0560004400) ' + D3BJ),
    'olyp': G09Protocol('OLYP'),
    'olyp-d3bj': G09Protocol('OLYP', D3BJ),
    'opbe': G09Protocol('OPBE'),
    'opbe-d3bj': G09Protocol('OPBE', D3BJ),
    'pbe': G09Protocol('PBE'),
    'pbe-d3bj': G09Protocol('PBE', D3BJ),
    'pbe0': G09Protocol('PBE0'),
    'pbe0-d3bj': G09Protocol('PBE0', D3BJ),
    'pbe38': G09Protocol('PBE'), #
    'pbe38-d3bj': G09Protocol('PBE'),
    'pbesol': G09Protocol('PBEPBE', 'iop(3/74=5050)'), #
    'pbesol-d3bj': G09Protocol('PBEPBE', 'iop(3/74=5050) ' + D3BJ),
    'ptpss': G09Protocol('PTPSS'), #
    'ptpss-d3bj': G09Protocol('PTPSS', D3BJ),
    'pw6b95': G09Protocol('PW6B95'), #
    'pw6b95-d3bj': G09Protocol('PW6B95', D3BJ),
    'pwb6k': G09Protocol('PWB6K'), #
    'pwb6k-d3bj': G09Protocol('PWB6K', D3BJ),
    'pwpb95': G09Protocol('PWPB95'),
    'pwpb95-d3bj': G09Protocol('PWPB95', D3BJ),
    's2-mp2': G09Protocol('MP2', redundancy='mp2'),
    'scs-mp2': G09Protocol('MP2', redundancy='mp2'),
    'sos-mp2': G09Protocol('MP2', redundancy='mp2'),
    'spw92': G09Protocol('SPW92'),
    'ssb': G09Protocol('SSB'),
    'ssb-d3bj': G09Protocol('SSB', D3BJ),
    'svwn': G09Protocol('SVWN'),
    'tpss': G09Protocol('TPSS'),
    'tpss-d3bj': G09Protocol('TPSS', D3BJ),
    'tpss0': G09Protocol('TPSS0'),
    'tpss0-d3bj': G09Protocol('TPSS0', D3BJ),
    'tpssh': G09Protocol('TPSSh'),
    'tpssh-d3bj': G09Protocol('TPSSh', D3BJ),
    'xyg3': G09Protocol('XYG3'),
    'xyg3-d3bj': G09Protocol('XYG3', D3BJ),
    'mpwlyp': G09Protocol('mPWLYP'),
    'mpwlyp-d3bj': G09Protocol('mPWLYP', D3BJ),
    'otpss': G09Protocol('oTPSS'),
    'otpss-d3bj': G09Protocol('oTPSS', D3BJ),
    'rpw86pbe': G09Protocol('rPW68PBE'),
    'rpw86pbe-d3bj': G09Protocol('rPW68PBE', D3BJ),
    'revpbe': G09Protocol('revPBE'),
    'revpbe-d3bj': G09Protocol('revPBE', D3BJ),
    'revpbe0': G09Protocol('revPBE0'),
    'revpbe0-d3bj': G09Protocol('revPBE0', D3BJ),
    'revpbe38': G09Protocol('revPBE38'),
    'revpbe38-d3bj': G09Protocol('revPBE38', D3BJ),
    'revssb': G09Protocol('revSSB'),
    'revssb-d3bj': G09Protocol('revSSB', D3BJ),
    'ωb97x-d': G09Protocol('wB97XD'),
}



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
        protocol = self.params['method'].lower()

        if not protocol in available_protocols:
            raise(UnknownProtocolError(self.params['method']))
        else:
            self.params['method'] = available_protocols[protocol]

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
            pass
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
