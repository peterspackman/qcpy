"""
    Parser for .xyz file formats
"""
from pathlib import Path
import logging

from qcauto.atom import Atom
from qcauto.coordinates import Coordinates
from qcauto.formats import FileFormatError, LineFormatError

LOG = logging.getLogger(__name__)


class XYZFile:
    """Object for an xyz file, constructed from a filename or a pathlib.Path object"""
    atoms = []
    number_of_atoms = 0
    filename = ""
    comment = ""

    def __init__(self, path):
        if not isinstance(path, Path):
            path = Path(path)
        self.filename = path.name

        with path.open('r') as xyz_file:
            self.atoms, self.comment = XYZFile.parse_lines(xyz_file.readlines())

    @staticmethod
    def parse_lines(lines, filename="lines"):
        """
        Parse a .xyz file line by line, returning a list of Atom and the comment string
        >>> XYZFile.parse_lines(['1', 'this is a comment line', "H 0.0 0.0 0.0"])
        ([H: [ 0.  0.  0.]], 'this is a comment line')
        """
        number_of_atoms = 0
        current_line = 0
        comment = ""
        atoms = []
        for i, line in enumerate(lines, 1):
            current_line = i
            if i == 1:
                number_of_atoms = int(line)
            elif i == 2:
                comment = line
            else:
                try:
                    atom = parse_atom_line(line)
                    atoms.append(atom)
                except(LineFormatError) as file_error:
                    raise FileFormatError(filename, current_line, file_error)
        if not len(atoms) == number_of_atoms:
            raise FileFormatError(filename,
                                  current_line,
                                  "incorrect number of atom lines (found {}, expected {})".format(
                                      len(atoms), number_of_atoms))

        return atoms, comment


    def __iter__(self):
        return iter(self.atoms)

    def __str__(self):
        return "XYZFile: {{{}}}".format(str(self.atoms))


def parse_atom_line(line, sep=" "):
    """ Parse a single line specifying an atom and its location
    >>> parse_atom_line("H 0.0 0.0 0.0")
    H: [ 0.  0.  0.]
    >>> parse_atom_line("C, 1.5, 3.2, 5", sep=", ")
    C: [ 1.5  3.2  5. ]
    """
    tokens = line.split(sep)
    if not len(tokens) == 4:
        msg = "incorrect number of tokens (found {}, expected {})".format(len(tokens), 4)
        raise LineFormatError(msg)
    center = float(tokens[1]), float(tokens[2]), float(tokens[3])

    try:
        atom = Atom.from_symbol_and_location(tokens[0], Coordinates(*center))
    except KeyError as key_error:
        raise LineFormatError(key_error)
    return atom
