"""All templates"""
import os
import logging
from jinja2 import Environment, FileSystemLoader, Template

LOG = logging.getLogger(__name__)
_ENV = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))))

GaussianSinglePointEnergy = _ENV.get_template('gaussian_spe.template')
TontoDFTSinglePointEnergy = _ENV.get_template('tonto_dft.template')
TontoRobyBondIndex = _ENV.get_template('tonto_roby.template')
GaussianWaveFunction = _ENV.get_template('gaussian_wave.template')
EmptyTemplate = _ENV.get_template('empty.template')

_ALL_TEMPLATES = {
        'gaussian_spe': GaussianSinglePointEnergy,
        'tonto_dft_spe': TontoDFTSinglePointEnergy,
        'tonto_roby': TontoRobyBondIndex,
        'gaussian_wfn': GaussianWaveFunction,
        'empty': EmptyTemplate,
}

def add_template(text=None, filename=None, name='new_template'):
    if filename:
        path, filename = os.path.split(filename)
        _ALL_TEMPLATES[name] = Environment(
            loader=FileSystemLoader(path or './')
            ).get_template(filename)
    elif text:
        _ALL_TEMPLATES[name] = Template(text)
    return _ALL_TEMPLATES[name]


def get_template(name):
    return _ALL_TEMPLATES.get(name, None)
