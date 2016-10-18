"""
Contains methods/classes for reading/writing all formats supported
by this library.
"""
__all__ = [
    "xyz",
    "gaussian"
]


class FileFormatError(Exception):
    """Indicates a file was malformatted"""
    def __init__(self, fname, line_number, message):
        super(FileFormatError, self).__init__(message)
        self.fname = fname
        self.line = line_number
        self.message = message

    def __str__(self):
        return "error reading {}, line {}: {}".format(self.fname,
                                                      self.line,
                                                      self.message)

class LineFormatError(Exception):
    """Indicates a line was malformatted"""
    def __init__(self, message):
        super(LineFormatError, self).__init__(message)
        self.message = message

    def __str__(self):
        return "while parsing line encountered {}".format(self.message)
   