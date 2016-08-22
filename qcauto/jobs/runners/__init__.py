import logging
from .localrunner import LocalRunner
log = logging.getLogger(__name__)


class NullRunner(object):
    """ Do nothing, return None"""
    _jobs = []

    def add_job(self, job):
        self._jobs.append(job)

    def run(self):
        while len(self._jobs) > 0:
            job = self._jobs.pop(0)
            if job.has_requirements():
                job.before_run()
            job.success = True
            yield job
