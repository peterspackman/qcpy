"""
    xyz.py

    Parser for .xyz file formats
"""
from pathlib import Path
from qcauto import Atom, Coordinates
from qcauto.formats import FileFormatError
import periodictable
import sys


class XYZFile():
    atoms = []
    n = 0
    filename = ""
    comment = ""
    _current_line = 0

    def __init__(self, path):
        if not isinstance(path, Path):
            path = Path(path)
        self.filename = path.name

        with path.open('r') as f:
            # Read number of atoms from line 1
            self.n = int(f.readline())
            self._current_line += 1
            # Read comment from line 2
            self.comment = f.readline()
            self._current_line += 1
            for i, line in enumerate(f.readlines()):
                self._current_line += 1
                try:
                    if i >= self.n:
                        raise FileFormatError(self.filename,
                                              self._current_line,
                                              "Too many atoms in file")
                    atom = self._parse_atom_line(line)
                except(FileFormatError) as e:
                    print(e)
                    return
                self.atoms.append(atom)

    def __str__(self):
        return(str(self.atoms))

    def _parse_atom_line(self, line):
        tokens = line.split()
        try:
            element = periodictable.elements.symbol(tokens[0])
        except KeyError:
            msg = "Unknown element symbol {}".format(tokens[0])
            raise FileFormatError(self.filename, self._current_line, msg)

        x, y, z = float(tokens[1]), float(tokens[2]), float(tokens[3])

        if len(tokens) > 4:
            msg = "Too many tokens on line ({})".format(len(center))
            raise FileFormatError(self.filename, self._current_line, msg)
        return Atom(element, Coordinates(x, y, z))
