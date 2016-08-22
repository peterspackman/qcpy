import logging
from qcauto.templates import EmptyTemplate
from qcauto import Geometry
log = logging.getLogger(__name__)


class Job(object):
    """ Abstract base class of Job """
    _name = "job"

    @property
    def name(self):
        return self._name

    def set_name(self, name):
        self._name = name


class InputFileJob(Job):
    """ Abstract base class of jobs with input/output files"""
    _input_file = "stdin"
    _template = EmptyTemplate

    def has_requirements(self):
        return True

    def write_input_file(self, filename):
        raise NotImplementedError

    def read_output_file(self, filename):
        raise NotImplementedError

class GeometryJob(Job):
    """ Abstract base class of job requiring a geometry """
    _geometry = None

    def geometry(self):
        return self._geometry
