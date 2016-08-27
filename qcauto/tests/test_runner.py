from qcauto.jobs.runners import LocalRunner
from qcauto.jobs.job import Job
from unittest import TestCase


class EchoJob(Job):
    _command = "echo {job.name}"

    def __init__(self, name):
        self._name = name

    @property
    def command(self):
        return self._command.format(job=self)


class TestEchoJob(TestCase):
    jobs = [EchoJob("first_job"), EchoJob("second_job")]
    runner = LocalRunner()

    def test_jobs_run(self):
        self.runner.add_jobs(self.jobs)
        for job, status in self.runner.run():
            assert status == True
            assert job.stdout.strip() == job.name
