import logging
from qcauto.templates import TontoRobyBondIndex
from .job import InputFileJob
log = logging.getLogger(__name__)


class TontoJob(InputFileJob):
    _basis_set = "3-21G"
    _method = "RHF"
    _name = "tonto_job"
    _input_file = 'stdin'
    _output_file = 'stdout'

    def write_input_file(self, filename):
        log.debug("Writing input file to {}".format(filename))
        with open(filename, 'w') as f:
            f.write(self._template.render(job=self))

    def before_run(self):
        self.write_input_file(self._input_file)

    def args(self):
        return []


class TontoRobyBondIndexJob(InputFileJob):
    fchk = "wavefunction.fchk"
    _template = TontoRobyBondIndex