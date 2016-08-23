import logging
from qcauto.templates import TontoRobyBondIndex
from .job import InputFileJob
log = logging.getLogger(__name__)


class TontoJob(InputFileJob):
    """ Abstract base class for tonto jobs"""
    _basis_set = "3-21G"
    _method = "RHF"
    _name = "tonto_job"
    _has_dependencies = True
    _requires_postprocessing = True

    def write_input_file(self, filename):
        log.debug("Writing input file to {}".format(filename))
        with open(filename, 'w') as f:
            f.write(self._template.render(job=self))

    def resolve_dependencies(self):
        log.debug("Resolving dependencies for tonto job {}".format(self.name))
        self.write_input_file(self.input_filename)

    def read_output_file(self, filename):
        pass


class TontoRobyBondIndexJob(TontoJob):
    _fchk_filename = "wavefunction.fchk"
    _template = TontoRobyBondIndex

    @property
    def fchk_filename(self):
        return self._fchk_filename

    def resolve_dependencies(self):
        assert os.path.exists(self.fchk)
        super().resolve_dependencies()
