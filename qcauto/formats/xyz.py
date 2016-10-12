"""
    Parser for .xyz file formats
"""
from pathlib import Path
import logging

from qcauto.atom import Atom
from qcauto.coordinates import Coordinates
from qcauto.formats import FileFormatError

LOG = logging.getLogger(__name__)


class XYZFile:
    """Object for an xyz file, constructed from a filename or a pathlib.Path object"""
    atoms = []
    number_of_atoms = 0
    filename = ""
    comment = ""
    _current_line = 0

    def __init__(self, path):
        if not isinstance(path, Path):
            path = Path(path)
        self.filename = path.name

        with path.open('r') as xyz_file:
            # Read number of atoms from line 1
            self.number_of_atoms = int(xyz_file.readline())
            self._current_line += 1
            # Read comment from line 2
            self.comment = xyz_file.readline()
            self._current_line += 1
            for i, line in enumerate(xyz_file.readlines()):
                self._current_line += 1
                try:
                    if i >= self.number_of_atoms:
                        raise FileFormatError(self.filename,
                                              self._current_line,
                                              "Too many atoms in file")
                    atom = self._parse_atom_line(line)
                except(FileFormatError) as file_error:
                    LOG.error(file_error)
                    return
                self.atoms.append(atom)

    def __iter__(self):
        return iter(self.atoms)

    def __str__(self):
        return "XYZFile: {{{}}}".format(str(self.atoms))

    def _parse_atom_line(self, line):
        tokens = line.split()
        if len(tokens) > 4:
            msg = "Too many tokens on line ({})"
            raise FileFormatError(self.filename, self._current_line, msg)
        center = float(tokens[1]), float(tokens[2]), float(tokens[3])

        try:
            atom = Atom.from_symbol_and_location(tokens[0], Coordinates(*center))
        except KeyError:
            msg = "Unknown atomic symbol: {}".format(tokens[0])
            raise FileFormatError(self.filename, self._current_line, msg)
        return atom
