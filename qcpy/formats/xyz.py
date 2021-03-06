"""
    Parser for .xyz file formats
"""
from pathlib import Path
import logging
import json

from ..atom import Atom
from ..coordinates import Coordinates
from . import FileFormatError, LineFormatError

LOG = logging.getLogger(__name__)


class XYZFile:
    """Object for an xyz file, constructed from a filename or a pathlib.Path object"""
    atoms = []
    number_of_atoms = 0
    filename = ""
    comment = ""

    def __init__(self, path, parse_comments=False):
        if not isinstance(path, Path):
            path = Path(path)
        self.filename = path.name

        with path.open('r') as xyz_file:
            self.atoms, self.comment = XYZFile.parse_lines(xyz_file.readlines(),
                                                           filename=self.filename)
        self.charge = 0
        self.multiplicity = 1
        if parse_comments:
            if self.comment.strip() != "":
                try:
                    comments = json.loads(self.comment)
                    self.charge = comments['charge']
                    self.multiplicity = comments['multiplicity']
                except Exception as e:
                    tokens = self.comment.split()
                    if len(tokens) == 2:
                        self.charge = int(tokens[0])
                        self.multiplicity = int(tokens[1])



    @staticmethod
    def parse_lines(lines, *, filename="lines"):
        """
        Parse a .xyz file line by line, returning a list of Atom and the comment string
        >>> XYZFile.parse_lines(['1', 'this is a comment line', "H 0.0 0.0 0.0"])
        ([H: [ 0.  0.  0.]], 'this is a comment line')
        """
        number_of_atoms = 0
        current_line = 0
        comment = ""
        atoms = []
        n, comment, *atom_lines = lines
        number_of_atoms = int(n.strip())
        for i, line in enumerate(atom_lines, 3):
            current_line = i
            if line.strip() != '':
                try:
                    atom = parse_atom_line(line.strip())
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


def parse_atom_line(line, **kwargs):
    """ Parse a single line specifying an atom and its location
    >>> parse_atom_line("H 0.0 0.0 0.0")
    H: [ 0.  0.  0.]
    >>> parse_atom_line("C, 1.5, 3.2, 5", sep=", ")
    C: [ 1.5  3.2  5. ]
    """
    tokens = line.split(**kwargs)
    if not len(tokens) == 4:
        msg = "incorrect number of tokens (found {}, expected {})".format(len(tokens), 4)
        raise LineFormatError(msg)
    center = float(tokens[1]), float(tokens[2]), float(tokens[3])
    if tokens[0] == 'D':
        tokens[0] = 'H'

    try:
        atom = Atom.from_symbol_and_location(tokens[0], Coordinates(*center))
    except KeyError as key_error:
        raise LineFormatError(key_error)
    return atom
