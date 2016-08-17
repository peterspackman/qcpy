import attr

@attr.s
class Job(object):

    def run(self):
        assert not hasattr(super(), 'program')

    def result(self):
        assert not hasattr(super(), 'program')
