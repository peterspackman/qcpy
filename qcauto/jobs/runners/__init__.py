import logging
from .localrunner import LocalRunner
log = logging.getLogger(__name__)

class NullRunner(object):
    """ Do nothing, return None"""

    def run(self, args=None):
        pass

    def result(self):
        return None

    def successful(self):
        return True
