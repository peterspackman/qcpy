"""
Contains class/methods to extract data from a g09 log file
"""
from pathlib import Path
import logging
import re
from . import FileFormatError, LineFormatError
from collections import defaultdict

HF_REGEX = re.compile(r'\\\s*H\s*F\s*=\s*([^\\]*)\\')
MP2_REGEX = re.compile(r'\\\s*M\s*\s*P\s*\s*2\s*=\s*([^\\]*)\\')
CONVERGENCE_FAIL_STRING = '>>>>>>>>>> Convergence criterion not met'

LOG = logging.getLogger(__name__)

class G09LogFile:
    """Object for an xyz file, constructed from a filename or a pathlib.Path object"""
    _filename = ""
    _contents = []
    _scf_energy = None
    _hf_energy = None
    _spin_components = None
    _cycles = None
    _converged = None

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
            text = ''.join(self.contents)
            match = re.search(HF_REGEX, text)
            if match:
                self._scf_energy = float(''.join(match.group(1).split()))

            match = re.search(MP2_REGEX, text)
            if match:
                self._scf_energy = float(''.join(match.group(1).split()))

            if not self._scf_energy:
                raise FileFormatError(self._filename, len(self.contents),
                                      "reached end of file without SCF energy")
        return self._scf_energy

    @property
    def converged(self):
        """Return whether or not this calculation converged"""
        did_not_converge = False
        energy_lines = []
        energies = []
        if self._converged is None:
            LOG.debug('Testing convergence in %s', self._filename)
            text = ''.join(self.contents)
            for line in self.contents:
                if line.startswith(' SCF Done'):
                    energy_lines.append(line)
                elif (CONVERGENCE_FAIL_STRING in line):
                    did_not_converge = True
            self._converged = True
            if did_not_converge:
                # only convert if we found a lack of convergence
                for line in energy_lines:
                    tokens = line.split('=')[1].split()
                    energies.append(float(tokens[0]))
                if len(energies) < 2:
                    self._converged = False
                # if there is more than a 30% difference between the two values
                # the convergence is not acceptable
                elif abs(1.0 - energies[1]/energies[0]) > 0.3:
                    self._converged = False
        return self._converged

    @property
    def hf_energy(self):
        """Return the SCF energy of this calculation,
        finding it in the log file if it is not already set"""
        if self._hf_energy is None:
            LOG.debug('Trying to find SCF energy in %s', self._filename)
            text = ''.join(self.contents)
            match = re.search(HF_REGEX, text)
            if match:
                self._hf_energy = float(''.join(match.group(1).split()))
            if not self._scf_energy:
                raise FileFormatError(self._filename, len(self.contents),
                                      "reached end of file without SCF energy")
        return self._hf_energy

    def scf_convergence(self):
        if self._cycles is None:
            LOG.debug('Trying to find scf_convergence in %s', self._filename)
            labels = []
            values = []
            for line in self._contents:
                if line.strip().startswith('Cycle'):
                    n = int(line.split()[1])
                if line.strip().startswith('E='):
                    energy = float(line.split()[1])
                    labels.append(n)
                    values.append(energy)
            self._cycles = labels, values
            if not self._cycles:
                raise FileFormatError(self._filename, len(self.contents),
                                      "reached end of file SCF finding SCF convergence")
        return self._cycles

    @staticmethod
    def parse_scf_energy_line(line):
        """Parse the SCF Done line in a g09 log file,
        returning the energy as a float"""
        tokens = line.split()
        return float(tokens[4])

    @staticmethod
    def parse_spin_component_line(line):
        tokens = line.strip().split()
        kind = tokens[0]
        LOG.debug('Tokens in spin component line%s', tokens)
        t2 = float(tokens[3].replace('D', 'E'))
        e2 = float(tokens[-1].replace('D', 'E'))
        return kind, t2, e2

    @property
    def mp2_spin_components(self):
        """Return the T(2) and E(2) spin components of this calculation,
        finding it in the log file if it is not already set"""
        if self._spin_components is None:
            self._spin_components = defaultdict(dict)
            LOG.debug('Trying to find T(2) and E(2) spin components in %s',
                      self._filename)
            for i, line in enumerate(self.contents, 1):
                if line.strip().startswith('Spin components'):
                    try:
                        for j in range(3):
                            kind, t2, e2 =\
                                    G09LogFile.parse_spin_component_line(self.contents[i + j])
                            self._spin_components[kind]['t2'] = t2
                            self._spin_components[kind]['e2'] = e2
                    except(LineFormatError) as line_error:
                        raise FileFormatError(self._filename, i, line_error)
                    break
            else:
                raise FileFormatError(self._filename, i,
                                      "reached end of file without SCF energy")
        return self._spin_components

