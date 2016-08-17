from unittest import TestCase
from qcauto.job import Job

class TestJob(TestCase):
    job = Job()

    def test_run(self):
        self.job.run()

    def test_result(self):
        self.job.result()
