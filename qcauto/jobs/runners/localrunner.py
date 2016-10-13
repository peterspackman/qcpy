"""
Run jobs on a local machine
"""
import logging
import subprocess
from .nullrunner import NullRunner
from qcauto.utils import working_directory
LOG = logging.getLogger(__name__)


class LocalRunner(NullRunner):
    """ Currently totally sequential """

    def run_job(self, job):
        LOG.debug('Starting %s', job.name)
        with working_directory(job.working_directory):
            kwargs = {
                'shell': job._requires_shell,
                'universal_newlines': True,
                'check': True,
            }

            if job.capture_stdout:
                kwargs['stdout'] = subprocess.PIPE
            if job.has_dependencies:
                job.resolve_dependencies()
            completed = subprocess.run(job.command, **kwargs)
            job._stdout = completed.stdout if job.capture_stdout else ""
            if job.requires_postprocessing:
                job.post_process()
        return completed.returncode == 0
