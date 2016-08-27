import logging
from .nullrunner import NullRunner
from qcauto.utils import working_directory
import subprocess
log = logging.getLogger(__name__)


class LocalRunner(NullRunner):
    """ Currently totally sequential """

    def run_job(self, job):
        log.debug('Starting {} '.format(job.name))
        with working_directory(job.working_directory):
            completed = subprocess.run(job.command, shell=True, check=True)
        return completed.returncode == 0
