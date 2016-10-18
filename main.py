#!/usr/bin/env python3
import argparse
import logging
from pathlib import Path
from qcpy.jobs import GaussianSinglePointEnergyJob as GaussianJob
from qcpy.jobs.runners import LocalRunner
from qcpy.geometry import Geometry

log = logging.getLogger('main')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dir')
    parser.add_argument('-l', '--log-level', default='ERROR',
                        help="Set the log level for this script")
    parser.add_argument('-b', '--basis-sets', nargs='+',
                        help='Basis sets to use for input file generation', required=True)
    parser.add_argument('-m', '--methods', nargs='+',
                        help='Methods to use for input file generation', required=True)
    parser.add_argument('-s', '--suffix', default='gjf',
                        help='g09 input file suffix to use')
    parser.add_argument('-n', '--name-string', default='{stem}-{method}-{basis_set}.{suffix}',
                        help='How to format names of input files')
    parser.add_argument('-o', '--output-dir', default='.',
                        help="Directory to put gaussian input files if 'basis' "
                             "is supplied as an argument, each different basis set "
                             "will have its own directory")
    parser.add_argument('-t', '--tonto', action='store_true',
                        help='Write tonto inputs instead')
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level)
    geometries = list(Path(args.dir).glob('*.xyz'))
    runner = LocalRunner()

    if len(geometries) < 1:
        log.error('No geometry files in %s', args.dir)

    for xyz_file in geometries:
        log.debug('reading geometry from %s', xyz_file)
        geometry = Geometry.from_xyz_file(xyz_file)
        log.debug('done reading geometry')

        for method in args.methods:
            for basis_set in args.basis_sets:
                name = xyz_file.stem
                job = GaussianJob(geometry, method=method, basis_set=basis_set)
                job.set_name(name)
                job.set_working_directory(job.name)
                runner.add_job(job)

    for job, exit_status in runner.run():
        print(job.name, job.method, job.basis_set)
        if exit_status:
            print(job.result)
        else:
            print('Failed')

if __name__ == '__main__':
    main()
