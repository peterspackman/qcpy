import os


class working_directory:
    """ Context manager for temporarily changing the current working directory. """

    def __init__(self, directory):
        if directory:
            self.directory = os.path.expanduser(directory)
        else:
            self.directory = None

    def __enter__(self):
        self.old_directory = os.getcwd()
        if self.directory:
            os.chdir(self.directory)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.old_directory)
