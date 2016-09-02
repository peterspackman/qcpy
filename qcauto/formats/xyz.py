"""
    xyz.py

    Parser for .xyz file formats
"""
from pathlib import Path
from qcauto.atom import Atom
from qcauto.coordinates import Coordinates
from qcauto.formats import FileFormatError
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

    def __iter__(self):
        return iter(self.atoms)

    def __str__(self):
        return(str(self.atoms))

    def _parse_atom_line(self, line):
        tokens = line.split()
        if len(tokens) > 4:
            msg = "Too many tokens on line ({})".format(len(center))
            raise FileFormatError(self.filename, self._current_line, msg)
        x, y, z = float(tokens[1]), float(tokens[2]), float(tokens[3])

        try:
            atom = Atom.from_symbol_and_location(tokens[0], Coordinates(x, y, z))
        except KeyError:
            msg = "Unknown atomic symbol: {}".format(tokens[0])
            raise FileFormatError(msg)
        return atom
