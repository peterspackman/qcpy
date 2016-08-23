import logging
from qcauto.templates import EmptyTemplate
from qcauto import Geometry
log = logging.getLogger(__name__)


class Job(object):
    """ Abstract base class of Job """
    _name = "job"
    _has_dependencies = False
    _requires_postprocessing = False

    @property
    def has_dependencies(self):
        """ Does this job require some work before it
        can be run?"""
        return self._has_dependencies

    @property
    def requires_postprocessing(self):
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
    def name(self):
        """ The name of the job as a string."""
        return self._name

    def set_name(self, name):
        """ Change the name of the job. """
        self._name = name


class InputFileJob(Job):
    """ Abstract base class of jobs with input/output files"""
    _input_filename = "stdin"
    _output_file = "stdout"
    _template = EmptyTemplate

    @property
    def input_filename(self):
        return self._input_filename

    @property
    def output_file(self):
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
