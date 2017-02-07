from qcpy.jobs.runners import LocalRunner
from qcpy.jobs.job import Job
from unittest import TestCase


class EchoJob(Job):
    _command = "echo {job.name}"
    _capture_stdout = True
    _requires_shell = True

    def __init__(self, name):
        self._name = name

    @property
    def command(self):
        return self._command.format(job=self)


class TestEchoJob(TestCase):
    jobs = [EchoJob("first_job"), EchoJob("second_job")]
    runner = LocalRunner()

    def test_jobs_run(self):
        """LocalRunner works for echo jobs"""
        self.runner.add_jobs(self.jobs)
        for job, status in self.runner.run():
            assert status == True
            assert job.stdout.strip() == job.name
