import attr
import os
import logging
from executor import execute
log = logging.getLogger(__name__)


def path_is_executable(instance, attribute, value):
    if not (os.path.isfile(value) and os.access(value, os.X_OK)):
        raise ValueError('{} is not an executable'.format(value))

@attr.s
class LocalRunner:
    executable_path = attr.ib(validator=path_is_executable)
    _success = attr.ib(default=False)
    _jobs = attr.ib(default=attr.Factory(list))

    def add_job(self, job):
        self._jobs.append(job)

    def run(self):
        while not len(self._jobs) == 0:
            job = self._jobs.pop(0)
            log.debug('Starting {} '.format(job.name))

            job.before_run()

            command = self.executable_path + ' ' + ' '.join(job.args())
            job.success = execute(command)

            job.after_run()
            log.debug('{} success: {}'.format(command, self._success))
            yield job
