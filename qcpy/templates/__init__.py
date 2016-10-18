"""All templates"""
import os
import logging
from jinja2 import Environment, FileSystemLoader

LOG = logging.getLogger(__name__)
_ENV = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))))

GaussianSinglePointEnergy = _ENV.get_template('gaussian_spe.template')
TontoDFTSinglePointEnergy = _ENV.get_template('tonto_dft.template')
TontoRobyBondIndex = _ENV.get_template('tonto_roby.template')
GaussianWaveFunction = _ENV.get_template('gaussian_wave.template')
EmptyTemplate = _ENV.get_template('empty.template')
