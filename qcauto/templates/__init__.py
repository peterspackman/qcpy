import attr
import os
import logging
from jinja2 import Environment, FileSystemLoader
_env = Environment(
        loader=FileSystemLoader(
            os.path.dirname(os.path.abspath(__file__))))

GaussianSinglePointEnergy = _env.get_template('gaussian_spe.template')
TontoDFTSinglePointEnergy = _env.get_template('tonto_dft.template')
