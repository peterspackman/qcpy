from unittest import TestCase
from qcauto.jobs.job import *
from qcauto.jobs import GaussianSinglePointEnergyJob, TontoRobyBondIndexJob
from .test_geometry import H2O


class TestJob:
    """ Base class for testing jobs """
    @property
    def name(self):
        return self._name

    @property
    def job(self):
        return self._job

    @property
    def geometry(self):
        return self._geometry

    def test_set_name_should_update_name(self):
        self.job.set_name(self.name)
        assert self.name == self.job.name


class TestTontoDFTJob(TestJob, TestCase):
    _name = "tonto_dft_job"
    _job = TontoRobyBondIndexJob()


class TestGaussianSinglePointEnergyJob(TestJob, TestCase):
    _name = "gaussian_energy_job"
    _geometry = H2O
    _job = GaussianSinglePointEnergyJob(_geometry)