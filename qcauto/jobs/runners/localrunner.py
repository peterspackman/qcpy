import logging
from .nullrunner import NullRunner
from executor import execute
log = logging.getLogger(__name__)


class LocalRunner(NullRunner):
    """ Currently totally sequential """

    def run_job(self, job):
        log.debug('Starting {} '.format(job.name))
        command = self.executable_path + ' ' + ' '.join(job.args())
        success = execute(command)
        return success
