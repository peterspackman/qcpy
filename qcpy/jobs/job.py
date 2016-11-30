"""
Abstract base classes for Jobs
"""
import logging

from ..templates import EmptyTemplate

LOG = logging.getLogger(__name__)


class Job(object):
    """ Abstract base class of Job """
    _name = "job"
    _has_dependencies = False
    _requires_postprocessing = False
    _working_directory = None
    _requires_shell = False
    _capture_stdout = False
    _stdout = ""
    _stderr = ""
    _result = None

    def set_working_directory(self, dirname: str):
        """"Set the working directory for this job"""
        self._working_directory = dirname

    @property
    def working_directory(self) -> str:
        """Return the current working directory for this job"""
        return self._working_directory

    @property
    def result(self):
        """Return the result of this calculation (varies)"""
        return self._result

    @property
    def stdout(self) -> str:
        """Return the output to stdout for this job"""
        return self._stdout

    @property
    def capture_stdout(self) -> bool:
        """Should this job capture what is written to stdout?"""
        return self._capture_stdout

    @property
    def has_dependencies(self) -> bool:
        """ Does this job require some work before it
        can be run?"""
        return self._has_dependencies

    @property
    def requires_postprocessing(self) -> bool:
        """ Does this job require some work after running? """
        return self._requires_postprocessing

    def resolve_dependencies(self):
        """ Do whatever needs to be done before running
        the job (e.g. write input file etc.)"""
        raise NotImplementedError

    def post_process(self):
        """ Do whatever needs to be done after the job."""
        raise NotImplementedError

    @property
    def name(self) -> str:
        """ The name of the job as a string."""
        return self._name

    def set_name(self, name: str):
        """ Change the name of the job. """
        self._name = name

    def __str__(self):
        return "{}: {}".format(self.__class__.__name__, self.name)

    def __repr__(self):
        return str(self)


class InputFileJob(Job):
    """ Abstract base class of jobs with input/output files"""
    _input_filename = "stdin"
    _output_file = "stdout"
    _template = EmptyTemplate
    _has_dependencies = True

    @property
    def input_filename(self) -> str:
        """What is the filename of the input file for this job?"""
        return self._input_filename

    @property
    def output_file(self) -> str:
        """What is the filename for the output file for this job?"""
        return self._output_file

    def render(self, **kwargs):
        """ Render the input file template.
        :returns the rendered template as a string."""
        return self._template.render(**kwargs)

    def write_input_file(self, filename):
        """ Write the input file to the filesystem.
        :param filename the name of the file as a string."""
        raise NotImplementedError

    def read_output_file(self, filename):
        """ Read the output file
        :param filename the path to the output file.
        """
        raise NotImplementedError


class GeometryJob(Job):
    """ Abstract base class of job requiring a geometry."""
    _geometry = None

    def geometry(self):
        """ The Geometry object for this job."""
        return self._geometry

    def resolve_dependencies(self):
        pass

    def post_process(self):
        pass
