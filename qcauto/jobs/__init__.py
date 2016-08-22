import attr
from .gaussian import GaussianJob, GaussianWaveFunctionJob
from .tonto import TontoRobyBondIndexJob

class Job(object):

    def before_run(self):
        pass

    def args(self):
        return []

    def after_run(self):
        pass
