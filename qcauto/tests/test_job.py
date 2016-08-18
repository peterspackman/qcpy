from unittest import TestCase
from qcauto.jobs import GaussianJob
from qcauto.jobs.runners import NullRunner
from .test_geometry import H2O


class TestJob(TestCase):
    job = GaussianJob(H2O, runner=NullRunner())

    def test_run(self):
        assert self.job.run() is None
