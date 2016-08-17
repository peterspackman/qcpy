from qcauto.jobs import Job
from qcauto.templates import GaussianSinglePointEnergy
log = logging.getLogger(__name__)

@attr.s
class GaussianJob(Job):
    geometry = attr.ib(validator=instance_of(Geometry))
    template = attr.ib(default=GaussianSinglePointEnergy)

    def write_input_file(self, filename):
        with open(filename, 'w') as f:
            f.write(self.template.render(geom=geometry))
            # gaussian needs a blank line at the end of the file
            f.write('\n')

    def run():
        pass

    def extract_gjf_energy(filename):
        with open(filename) as f:
            for line in f:
                if 'SCF Done' in line:
                    return float(re.findall('[-+]\d+[\.]?\d*', line)[0])

