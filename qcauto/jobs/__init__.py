import attr
from .gaussian import GaussianJob

class Job(object):

    def before_run(self):
        pass

    def args(self):
        return []

    def after_run(self):
        pass
