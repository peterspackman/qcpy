"""
Contains class/methods to extract data from a g09 log file
"""
from pathlib import Path
import logging
from qcpy.formats import FileFormatError, LineFormatError

LOG = logging.getLogger(__name__)

class G09LogFile:
    """Object for an xyz file, constructed from a filename or a pathlib.Path object"""
    _filename = ""
    _contents = []
    _scf_energy = None

    def __init__(self, path):
        if not isinstance(path, Path):
            path = Path(path)
        self._filename = path.name

        with path.open('r') as log_file:
            self._contents = log_file.readlines()
    @property
    def contents(self):
        """Return the contents of this file as lines"""
        return self._contents

    @property
    def scf_energy(self):
        """Return the SCF energy of this calculation,
        finding it in the log file if it is not already set"""
        if self._scf_energy is None:
            LOG.debug('Trying to find SCF energy in %s', self._filename)
            for i, line in enumerate(self.contents, 1):
                if line.startswith(' SCF Done:'):
                    try:
                        self._scf_energy = G09LogFile.parse_scf_energy_line(line)
                    except(LineFormatError) as line_error:
                        raise FileFormatError(self._filename, i, line_error)
                    break
            else:
                raise FileFormatError(self._filename, i,
                                      "reached end of file without SCF energy")
        return self._scf_energy

    @staticmethod
    def parse_scf_energy_line(line):
        """Parse the SCF Done line in a g09 log file,
        returning the energy as a float"""
        tokens = line.split()
        return float(tokens[4])
