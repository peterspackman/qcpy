#!/usr/bin/env python3
import attr
import logging
log = logging.getLogger(__name__)

@attr.s
class Job(object):

    def run(self):
        assert not hasattr(super(), 'program')

    def result(self):
        assert not hasattr(super(), 'program')
