#!/usr/bin/env python3
import logging
import sys
from qcauto.jobs import GaussianSinglePointEnergyJob as GaussianJob
from qcauto.jobs.runners import LocalRunner
from qcauto.geometry import Geometry
from qcauto.tests.test_geometry import H2O


def main():
    log_level='INFO'
    if len(sys.argv) > 1:
        log_level = sys.argv[1]
    logging.basicConfig(level=log_level)

    geom = H2O
    runner = LocalRunner()

    for method in ['HF', 'BLYP', 'BVWN5']:
        for basis_set in ['STO-3G', '3-21G']:
            name = 'h2o'
            job = GaussianJob(geom, basis_set=basis_set, method=method)
            job.set_name(name)
            runner.add_job(job)

    for job, exit_status in runner.run():
        print(job.name, job.method, job.basis_set, job.result)

if __name__ == '__main__':
    main()
