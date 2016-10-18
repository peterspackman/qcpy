from collections import deque
import logging

log = logging.getLogger(__name__)


class NullRunner(object):
    """ Do nothing for each job, returning True
    for job success status. """
    _jobs = deque()

    def add_job(self, job):
        log.debug("Adding {} to job queue.".format(job.name))
        self._jobs.append(job)

    def add_jobs(self, jobs):
        for job in jobs:
            self.add_job(job)

    def run_job(self, job):
        return True

    def run(self, resolve_dependencies=False):
        log.debug("Running all jobs in job queue.")
        while self._jobs:
            job = self._jobs.popleft()
            log.debug("Starting {}".format(job.name))
            if resolve_dependencies and job.has_dependencies:
                job.resolve_dependencies()
            success = self.run_job(job)
            yield (job, success)
