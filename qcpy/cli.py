from tqdm import tqdm
import argparse
import logging
import json
import os
from pathlib import Path
from qcpy.geometry import Geometry
from qcpy.jobs.gaussian import available_protocols, GaussianJob
from qcpy.formats.gaussian import G09LogFile
from collections import defaultdict

LOG_FORMAT = '[%(name)s]: %(message)s'
LOG = logging.getLogger(__name__)

benchmark_protocols = {
    'LDA': [
        'svwn5', 'svwn'
    ],
    'GGA': [
        'blyp', 'b97', 'b97d', 'hcth407', 'pbepbe',
        'bp86', 'bpw91', 'sogga11', 'n12'
    ],
    'MGGA': [
        'mo6l', 'tpsstpss', 'thcth', 'vsxc', 'bb95',
        'm11l', 'mn12l', 'mn15l'
    ],
    'HGGA': [
        'bhandhlyp', 'b3lyp', 'o3lyp', 'x3lyp',
        'b3p86', 'b3pw91', 'pbe1pbe', 'pbeh1pbe',
        'b971', 'b98', 'sogga11x', 'apf', 'apfd',
        'mpw1pw91', 'mpw1lyp', 'mpw1pbe', 'mpw3pbe',
        'mpw3pbe', 'hseh1pbe', 'ohse2pbe'
    ],
    'HMGGA': [
        'm05', 'm052x', 'm06', 'm062x', 'm06hf',
        'bmk', 'b1b95', 'tpssh', 'thcthhyb', 'pw6b95',
        'm08hx', 'mn15'
    ],
    'RS': [
        'cam-b3lyp', 'lc-wpbe', 'lc-whpbe', 'wb97', 'wb97x',
        'wb97xd', 'n12sx', 'm11', 'mn12sx', 'lc-blyp', 'lc-pbepbe',
        'lc-bp86', 'lc-bpw91'
    ],
    'AI': [
        'hf', 'mp2', 'scs-mp2', 'sos-mp2', 's2-mp', 'scs(mi)-mp2',
        'scs-mp2-vdw'
    ]
}

already_dispersion_corrected = ['b97d', 'apfd', 'wb97xd', 'dsdpbep86']

def read_benchmark_info(filename):
    """Read info.json"""
    with open(filename) as f:
        return json.load(f)


def write_benchmark_info(filename, benchmark_info):
    with open(filename, 'w') as f:
        json.dump(benchmark_info, f,
                sort_keys=True,
                indent=4, 
                separators=(',', ': '))


def read_systems(path, required_geometries, prefix='', suffix='.xyz'):
    """Add the systems to the database"""
    app_root = 'qcdb'
    systems = {}
    geometry_files = list(map(lambda x: Path(path, x).with_suffix(suffix), required_geometries))
    with tqdm(total=len(geometry_files), unit='xyz', desc='Reading geometries') as pbar:
        for f in geometry_files:
            geometry = Geometry.from_xyz_file(f, parse_comments=True)
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
    io = Path(root, 'calcs')
    skipped = defaultdict(list)

    if not io.exists():
        io.mkdir()

    all_methods = sorted({x for value in benchmark_protocols.values() for x in value})

    with tqdm(total=len(systems) * len(all_methods),
              desc='Writing input files',
              unit='gjf') as pbar:
        sys = systems.items()
        for protocol_name in all_methods:
            protocol = available_protocols[protocol_name]
            if protocol.redundancy is None:
                path = io / Path(protocol_name)
                if not path.exists():
                    path.mkdir()
                for name, geom in sys:
                    job = GaussianJob(name='{} {}/{}'.format(name,
                                                             protocol_name,
                                                             basis_set),
                                      method=protocol_name, geometry=geom, basis_set=basis_set) 
                    filename = str(path / Path(name+'.gjf')) 
                    job.write_input_file(filename)
                    pbar.update(1)
            else:
                skipped[protocol.redundancy].append(protocol_name)
                pbar.update(len(sys))
    for k, v in skipped.items():
        LOG.info('Skipping %s: calculation would be redundant when performing %s', ', '.join(v), k)
    return skipped

def read_outputs(directories, suffix='.log', expected=1):
    energies = defaultdict(dict)
    for d in directories:
        log_files = list(d.glob('*{}'.format(suffix)))
        if len(log_files) < expected:
            LOG.warn('Less log files than expected in %s (%d/%d)',
                     d, len(log_files), 4)
        for f in log_files:
            l = G09LogFile(f)
            energies[d.name][f.stem] = l.scf_energy
            LOG.info('Energy %s = %g', str(f), l.scf_energy)
    return energies


def get_required_geometries(benchmark_info, suffix='.xyz'):
    required_geometries = set()
    for r in benchmark_info['reactions'].values():
        required_geometries = required_geometries.union(
                set(r['reactants'][1] + r['products'][1]))
    required_geometries = set(map(lambda x: x.rstrip(suffix), required_geometries))
    return required_geometries




def generate_inputs():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', default='.', 
                        help='Path in which to look for input')
    parser.add_argument('-b', '--basis-set', default='def2qzvpp',
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
    required_geometries = get_required_geometries(benchmark_info, suffix=args.file_suffix)
    LOG.info('%d geometry files required for all reactions', len(required_geometries))

    systems = read_systems(Path(args.directory),
                           required_geometries,
                           prefix=benchmark_info['benchmark'],
                           suffix=args.file_suffix)
    read_reactions(benchmark_info['reactions'], systems, prefix=benchmark_info['benchmark'], suffix=args.file_suffix)
    skipped = create_input_files(args.directory, systems, args.basis_set)
    benchmark_info['post process'] = skipped
    write_benchmark_info(info_file, benchmark_info)

def process_outputs():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', default='.', 
                        help='Path in which to look for input')
    parser.add_argument('-s', '--file-suffix', default='.log',
                        help="Suffix when looking for output files")
    parser.add_argument('--log-level', default='WARN',
                        help='Level of log info to display')
    args = parser.parse_args()
    logging.basicConfig(format=LOG_FORMAT, level=args.log_level)

    info_file = Path(args.directory, 'info.json')
    benchmark_info = read_benchmark_info(info_file)
    required_geometries = get_required_geometries(benchmark_info)

    subdirs = [p for p in Path(args.directory, 'calcs').iterdir() if p.is_dir()]
    energies = read_outputs(subdirs, expected=len(required_geometries))