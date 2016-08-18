__all__ = [
        "xyz",
]


class FileFormatError(Exception):
    def __init__(self, fname, line_number, message):
        self.fname = fname
        self.line = line_number
        self.message = message

    def __str__(self):
        return "Error reading '{}'\nLine {}: {}".format(self.fname,
                                                        self.line,
                                                        self.message)
