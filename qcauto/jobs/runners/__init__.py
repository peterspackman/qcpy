import logging
from .localrunner import LocalRunner
log = logging.getLogger(__name__)

class NullRunner(object):

    def run(self):
        pass

    def result(self):
        return None
