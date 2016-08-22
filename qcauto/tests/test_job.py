from unittest import TestCase
from qcauto.jobs import GaussianSinglePointEnergyJob, TontoRobyBondIndexJob
from .test_geometry import H2O


class TestJob(TestCase):
    gaussian_job = GaussianSinglePointEnergyJob(H2O)
    tonto_job = TontoRobyBondIndexJob()

    def test_name(self):
        assert self.gaussian_job.name == "gaussian_job"
