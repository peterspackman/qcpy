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
        """set_name propagates correctly"""
        self.job.set_name(self.name)
        self.assertEqual(self.name, self.job.name)


class TestTontoJob(JobCommon, TestCase):
    _name = "tonto_scf_job"
    _geometry = H2O
    _job = TontoJob(_geometry)

    def test_dependencies_exist(self):
        """tonto jobs depend on input files"""
        self.assertTrue(self.job.has_dependencies)

    def test_set_basis_set(self):
        """tonto set valid basis set"""
        valid_basis = 'cc-pVDZ'
        self.job.set_basis_set(valid_basis)
        self.assertEqual(self.job.basis_set, valid_basis)

    def test_set_basis_set_raises(self):
        """tonto set invalid basis set raises exception"""
        invalid_basis = 'cc-pV6Z'
        with self.assertRaises(InvalidBasisSetName):
            self.job.set_basis_set(invalid_basis)


class TestGaussianSinglePointEnergyJob(JobCommon, TestCase):
    _name = "gaussian_energy_job"
    _geometry = H2O
    _job = GaussianSinglePointEnergyJob(_geometry)

    def test_dependencies_exist(self):
        """g09 jobs depend on input file"""
        self.assertTrue(self.job.has_dependencies)
