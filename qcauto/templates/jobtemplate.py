from jinja2 import Environment, FileSystemLoader
import os

env = Environment(loader=FileSystemLoader(
    os.path.dirname(os.path.abspath(__file__))))

@attr.s
class JobTemplate:
    input_file = attr.ib("job.input")
    output_file = attr.ib("job.output")

gjf_template = env.get_template('h2o.gjf.template')
tonto_template = env.get_template('stdin.template')
