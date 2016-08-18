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

    def run(self, args):
        command = self.executable_path + ' ' + ' '.join(args)
        log.debug('Starting {} '.format(command))
        self._success = execute(command)
        log.debug('{} success: {}'.format(command, self._success))

    def successful(self):
        return self._success

    def result(self):
        return self._success
