from unittest import TestCase
from qcpy.jobs.job import *
from qcpy.jobs import GaussianSinglePointEnergyJob, TontoJob
from .test_geometry import H2O


class JobCommon:
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


class TestTontoJob(JobCommon, TestCase):
    _name = "tonto_scf_job"
    _geometry = H2O
    _job = TontoJob(_geometry)

    def test_dependencies_exist(self):
        assert self.job.has_dependencies


class TestGaussianSinglePointEnergyJob(JobCommon, TestCase):
    _name = "gaussian_energy_job"
    _geometry = H2O
    _job = GaussianSinglePointEnergyJob(_geometry)

    def test_dependencies_exist(self):
        assert self.job.has_dependencies
