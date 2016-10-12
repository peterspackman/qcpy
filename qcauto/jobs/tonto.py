"""All tonto job classes"""
import logging
from qcauto.templates import TontoRobyBondIndex as Roby
from qcauto.templates import TontoDFTSinglePointEnergy as DFT
from .job import InputFileJob
LOG = logging.getLogger(__name__)


class TontoJob(InputFileJob):
    """ Abstract base class for tonto jobs"""
    _basis_set = "3-21G"
    _method = "RHF"
    _name = "tonto_job"
    _has_dependencies = True
    _requires_postprocessing = True
    _template = DFT

    def write_input_file(self, filename):
        LOG.debug("Writing input file to %s", filename)
        with open(filename, 'w') as input_file:
            input_file.write(self._template.render(job=self))

    def resolve_dependencies(self):
        LOG.debug("Resolving dependencies for tonto job %s", self.name)
        self.write_input_file(self.input_filename)

    def read_output_file(self, filename):
        pass

    def post_process(self):
        pass


class TontoRobyBondIndexJob(TontoJob):
    """Class to run roby bond index jobs"""
    _fchk_filename = "wavefunction.fchk"
    _template = Roby

    @property
    def fchk_filename(self):
        """Returns the fchk filename for this job"""
        return self._fchk_filename

    def resolve_dependencies(self):
        import os
        assert os.path.exists(self.fchk_filename)
        super().resolve_dependencies()
