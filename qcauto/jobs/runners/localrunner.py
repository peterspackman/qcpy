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
    args = attr.ib(default=attr.Factory(list))

    def run(self):
        log.info('Starting {} '.format(executable_path))
        return execute(executable_path)
