"""All templates"""
import os
import logging
from jinja2 import Environment, FileSystemLoader, Template

LOG = logging.getLogger(__name__)
_ENV = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))))

GaussianSCF = _ENV.get_template('gaussian_scf.template')
TontoSCF = _ENV.get_template('tonto_scf.template')
EmptyTemplate = _ENV.get_template('empty.template')

_ALL_TEMPLATES = {
        'gaussian_scf': GaussianSCF,
        'tonto_scf': TontoSCF,
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
