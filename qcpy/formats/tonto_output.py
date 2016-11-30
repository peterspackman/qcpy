from pathlib import Path
import logging
from . import FileFormatError, LineFormatError
import re

LOG = logging.getLogger(__name__)

class TontoOutputFile:
    """Object for a tonto output file, constructed from a filename or a pathlib.Path object"""
    _filename = ""
    _contents = []
    _scf_energy = None
    _data = None

    def __init__(self, path):
        if not isinstance(path, Path):
            path = Path(path)
        self._filename = path.name

        with path.open('r') as stdout_file:
            self._contents = stdout_file.readlines()

    @property
    def contents(self):
        """Return the contents of this file as lines"""
        return self._contents

    @property
    def structured_contents(self):
        """Return the structured data parsed from this file"""
        if not self._data:
            self._parse()
        return self._data

    def _get_sections(self):
        string = ''.join(self.contents)
        sections = re.findall(r"=+\n([^\r\n]*)\n=+([^=]*)", string)
        section_data = {}
        for section in sections:
            section_data[section[0]] = self._parse_section(section[1].strip())
        self._data = section_data

    def _parse_section(self, string):
        return dict(re.findall('(.*)\s\.+\s(.*)', string))

    def _parse(self):
        self._get_sections()
        self._cleanup_structured_data()

    def _cleanup_structured_data(self):
        for section, contents in self._data.items():
            self._data[section] = dict((k, v.strip()) for k, v in contents.items() if v)
