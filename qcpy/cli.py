from tqdm import tqdm
import argparse
import logging
import json
import os
from pathlib import Path
from qcpy.geometry import Geometry
from qcpy.jobs.gaussian import available_protocols, GaussianJob
from collections import defaultdict

LOG_FORMAT = '[%(name)s]: %(message)s'
LOG = logging.getLogger(__name__)


def read_benchmark_info(filename):
    """Read info.json"""
    with open(filename) as f:
        return json.load(f)


def read_systems(path, required_geometries, prefix='', suffix='.xyz'):
    """Add the systems to the database"""
    app_root = 'qcdb'
    systems = {}
    geometry_files = list(map(lambda x: Path(path, x).with_suffix(suffix), required_geometries))
    with tqdm(total=len(geometry_files), unit='xyz', desc='Reading geometries') as pbar:
        for f in geometry_files:
            geometry = Geometry.from_xyz_file(f)
            systems[f.name.strip(suffix)] = geometry
            pbar.update(1)
    return systems


def read_reactions(reactions, systems, prefix='', suffix='.xyz'):
    """Add the Reaction, Reagent etc. database entities from the supplied input"""
    for reaction, info in reactions.items():
        LOG.debug('Reaction: %s', reaction)
        sys_names = info['reactants'][1] + info['products'][1]
        reaction_systems = [systems[x.rstrip(suffix)] for x in sys_names]
        LOG.debug('Reaction systems: %s', reaction_systems)
        stoichiometry = [-x for x in info['reactants'][0]] + info['products'][0]


def create_input_files(root, systems, basis_set):
    LOG.debug('Systems = %s', systems)
    io = Path(root, 'io')
    skipped = defaultdict(list)

    if not io.exists():
        io.mkdir()

    with tqdm(total=len(systems) * len(available_protocols.keys()),
              desc='Writing input files',
              unit='gjf') as pbar:
        sys = systems.items()
        for protocol_name, protocol in available_protocols.items():
            if protocol.redundancy is None:
                path = io / Path(protocol_name)
                if not path.exists():
                    path.mkdir()
                for name, geom in sys:
                    job = GaussianJob(method=protocol_name, geometry=geom, basis_set=basis_set) 
                    filename = str(path / Path(name+'.gjf')) 
                    job.write_input_file(filename)
                    pbar.update(1)
            else:
                skipped[protocol.redundancy].append(protocol_name)
                pbar.update(len(sys))
    for k, v in skipped.items():
        LOG.info('Skipping %s: calculation would be redundant when performing %s', ', '.join(v), k)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', default='.', 
                        help='Path in which to look for input')
    parser.add_argument('-b', '--basis-set', default='def2-QZVP',
                        help='Basis set for input file jobs')
    parser.add_argument('--dry-run', default=True, action='store_false',
                        help="Print what will be done, but don't actually do anything")
    parser.add_argument('-s', '--file-suffix', default='.xyz',
                        help="Suffix when looking for geometry files")
    parser.add_argument('--log-level', default='WARN',
                        help='Level of log info to display')
    args = parser.parse_args()

    logging.basicConfig(format=LOG_FORMAT, level=args.log_level)
    info_file = Path(args.directory, 'info.json')
    LOG.debug('Reading benchmark file from %s', info_file)
    benchmark_info = read_benchmark_info(info_file)
    required_geometries = set()
    for r in benchmark_info['reactions'].values():
        required_geometries = required_geometries.union(
                set(r['reactants'][1] + r['products'][1]))
    required_geometries = set(map(lambda x: x.rstrip(args.file_suffix), required_geometries))

    LOG.info('%d geometry files required for all reactions', len(required_geometries))

    systems = read_systems(Path(args.directory),
                           required_geometries,
                           prefix=benchmark_info['benchmark'],
                           suffix=args.file_suffix)
    read_reactions(benchmark_info['reactions'], systems, prefix=benchmark_info['benchmark'], suffix=args.file_suffix)
    create_input_files(args.directory, systems, args.basis_set)
