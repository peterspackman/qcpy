from tqdm import tqdm
import argparse
import logging
import toml
import os
from pathlib import Path
from qcpy.geometry import Geometry
from qcpy.jobs.gaussian import available_protocols, GaussianJob

LOG = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'basis_set': 'def2-QZVP',
    'functionals': ['B3LYP', 'BLYP', 'PBE0'],
    'images_path': '/static/images'
}

def read_benchmark_info(filename):
    """Read info.toml"""
    return toml.load(str(filename))

def read_systems(path, prefix='', suffix='.xyz'):
    """Add the systems to the database"""
    app_root = 'qcdb'
    systems = {}
    for f in tqdm(list(path.glob('*{}'.format(suffix)))):
        geometry = Geometry.from_xyz_file(f)
        systems[f.name.strip(suffix)] = geometry
        LOG.debug('Adding new system: %s', geometry)
    return systems


def read_reactions(reactions, systems, prefix='', suffix='.xyz'):
    """Add the Reaction, Reagent etc. database entities from the supplied input"""
    for reaction, info in reactions.items():
        LOG.debug('Reaction: %s', reaction)
        sys_names = info['reagents'][1] + info['products'][1]
        reaction_systems = [systems[x.rstrip(suffix)] for x in sys_names]
        LOG.debug('Reaction systems: %s', reaction_systems)
        stoichiometry = [-x for x in info['reagents'][0]] + info['products'][0]


def create_input_files(root, systems, basis_set):
    LOG.debug('Systems = %s', systems)
    io = Path(root, 'io')

    if not io.exists():
        io.mkdir()

    for protocol in available_protocols.keys():
        path = io / Path(protocol)
        if not path.exists():
            path.mkdir()
        for name, geom in tqdm(systems.items()):
            job = GaussianJob(method=protocol, geometry=geom, basis_set=basis_set) 
            filename = str(path / Path(name+'.gjf')) 
            LOG.info('Writing input file to %s', filename)
            job.write_input_file(filename)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', default='.', 
                        help='Path in which to look for input')
    parser.add_argument('-b', '--basis-set', default='cc-pVDZ',
                        help='Basis set for input file jobs')
    parser.add_argument('--dry-run', default=True, action='store_false',
                        help="Print what will be done, but don't actually do anything")
    parser.add_argument('-s', '--file-suffix', default='.xyz',
                        help="Suffix when looking for geometry files")
    parser.add_argument('--log-level', default='INFO',
                        help='Level of log info to display')
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)

    benchmark_info = read_benchmark_info(Path(args.directory, 'info.toml'))
    LOG.debug(benchmark_info)
    systems = read_systems(Path(args.directory), prefix=benchmark_info['benchmark'], suffix=args.file_suffix)
    read_reactions(benchmark_info['reactions'], systems, prefix=benchmark_info['benchmark'], suffix=args.file_suffix)
    create_input_files(args.directory, systems, args.basis_set)
