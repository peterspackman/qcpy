from tqdm import tqdm
import argparse
import logging
import json
import os
import shutil
import time
import sys
from pathlib import Path
from qcpy.geometry import Geometry
from qcpy.jobs.gaussian import available_methods, GaussianJob
from qcpy.formats.gaussian import G09LogFile
from qcpy.formats import FileFormatError
from qcpy.utils import scs_e2_correction
from collections import defaultdict

HAVE_DFTD3_CORRECTION = False
try:
    from dftd3 import d3_correction, parameters
    HAVE_DFTD3_CORRECTION = True
except Exception as e:
    pass

LOG_FORMAT = '[%(name)s]: %(message)s'
LOG = logging.getLogger(__name__)

benchmark_methods = {
    'LDA': [
        'svwn5'
    ],
    'GGA': [
        'blyp', 'b97', 'b97d', 'hcth407', 'pbepbe',
        'bp86', 'bpw91', 'sogga11', 'n12'
    ],
    'MGGA': [
        'm06l', 'tpsstpss', 'thcth', 'vsxc', 'bb95',
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
    'DH': [
        'b2gpplyp', 'b2kplyp', 'b2tplyp', 'dsd-blyp', 'dsd-pbep86'
    ],
    'RS': [
        'cam-b3lyp', 'lc-wpbe', 'lc-whpbe', 'wb97', 'wb97x',
        'wb97xd', 'n12sx', 'm11', 'mn12sx', 'lc-blyp', 'lc-pbepbe',
        'lc-bp86', 'lc-bpw91'
    ],
    'HF': [
        'hf',
    ],
    'POSTHF': [
        'mp2', 'scs-mp2', 'sos-mp2', 's2-mp', 'scs(mi)-mp2',
        'scs-mp2-vdw', 'scsn-mp2'
    ]
}

def rsuffix(s, suffix):
    if s.endswith(suffix):
        return s[:-len(suffix)]
    return s

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


def guess_geometry_dir(path):
    for guess in ['xyz', 'XYZ', 'geoms', 'GEOMS']:
        path_guess = Path(path, guess)
        if path_guess.exists() and path_guess.is_dir():
            return path_guess
    return None

def read_systems(path, required_geometries, *, prefix='', suffix='.xyz', copy_to=None, progress=True):
    """Add the systems to the database"""
    app_root = 'qcdb'
    systems = {}
    geometry_dir = guess_geometry_dir(path)

    if geometry_dir is None:
        LOG.error('Could not locate geometries')
        return None

    geometry_files = list(map(lambda x: Path(geometry_dir, x+'.xyz'), required_geometries))
    with tqdm(total=len(geometry_files), unit='systems', desc='Reading geometries', disable=(not progress)) as pbar:
        for f in geometry_files:
            geometry = Geometry.from_xyz_file(f, parse_comments=True)
            systems[f.stem] = geometry

            if copy_to is not None:
                shutil.copy(f, copy_to)
            pbar.update(1)
    return systems


def read_reactions(reactions, systems, *, prefix='', suffix='.xyz'):
    """Add the Reaction, Reagent etc. database entities from the supplied input"""
    r = {}
    for reaction, info in reactions.items():
        LOG.debug('Processing reaction %s', reaction)
        sys_names = info['reactants'][1] + info['products'][1]
        LOG.debug('systems: %s', sys_names)
        reaction_systems = [systems[rsuffix(x,suffix)] for x in sys_names]
        LOG.debug('Contains %s', reaction_systems)
        stoichiometry = [-x for x in info['reactants'][0]] + info['products'][0]
        r[reaction] = [(rsuffix(s, suffix), r) for s, r in zip(sys_names, stoichiometry)]
    return r


def create_input_files(root, systems, basis_set, *, progress=True):
    LOG.debug('Systems = %s', systems)
    io = Path(root, 'calcs')
    skipped = defaultdict(list)

    if not io.exists():
        io.mkdir()

    all_methods = sorted({x for value in benchmark_methods.values() for x in value})

    with tqdm(total=len(systems) * len(all_methods),
              desc='Writing input files',
              unit='gjf',
              disable=(not progress)) as pbar:
        sys = systems.items()
        for method_name in all_methods:
            method = available_methods[method_name]
            if method.redundancy is None:
                path = io / Path(method_name)
                if not path.exists():
                    path.mkdir()
                for name, geom in sys:
                    job = GaussianJob(name='{} {}/{}'.format(name,
                                                             method_name,
                                                             basis_set),
                                      method=method_name, geometry=geom, basis_set=basis_set) 
                    filename = str(path / Path(name+'.gjf')) 
                    job.write_input_file(filename)
                    pbar.update(1)
            else:
                skipped[method.redundancy].append(method_name)
                pbar.update(len(sys))
    for k, v in skipped.items():
        LOG.info('Skipping %s: calculation would be redundant when performing %s', ', '.join(v), k)
    return skipped


def add_d3_correction_value(l, method_name, system_name, method, energies, systems):
    """Add a dispersion corrected value if necessary"""
    if not (method.includes_dispersion or \
            method_name in already_dispersion_corrected):
        try:
            s = systems[system_name]
        except KeyError as e:
            LOG.error('Could not find file %s', f)
            sys.exit(1)
        if method_name in parameters['bj'].keys():
            d3, _ = d3_correction(s.as_atomic_numbers(),
                                  s.as_coordinate_matrix(units='bohr'),
                                  func=method_name)
            LOG.debug("Dispersion correction for %s (%s): %s hartree",
                      system_name, method_name, d3)
            energies[method_name + ' + d3(bj)'][system_name] = l.scf_energy + d3
        else:
            LOG.debug('No parameters for %s', method_name)


def add_mp2_variants(system_name, l, energies):
    dependents = {n: p for n, p in available_methods.items() if p.redundancy == 'mp2'}
    e_hf = l.hf_energy
    sc = l.mp2_spin_components
    LOG.debug('E(%s,mp2) = %s', system_name, l.scf_energy)
    for method, method in dependents.items():
        correction = scs_e2_correction(sc, **method.correction)
        energies[method][system_name] = e_hf + correction
        LOG.debug('E(%s,%s) = %s + %s = %s', system_name, method, e_hf,
                  correction, energies[method][system_name])


def read_outputs(directories, systems, pbar, *, suffix='.log', expected=1):
    energies = defaultdict(dict)

    for d in directories:
        log_files = [f for f in d.iterdir() if f.name.endswith(suffix)]
        method_name = d.name

        if len(log_files) < expected:
            LOG.warn('Less log files than expected in %s (%d/%d)',
                     d, len(log_files), expected)
        try:
            proto = available_methods[method_name]
        except KeyError as e:
            LOG.warn('Unknown method %s', method_name)
            continue
        for f in log_files:
            l = G09LogFile(f)
            system_name = f.stem
            if l.converged:
                try:
                    energies[method_name][system_name] = l.scf_energy
                    if HAVE_DFTD3_CORRECTION:
                        add_d3_correction_value(l, method_name, system_name, proto, energies, systems)
                        
                    if method_name == 'mp2':
                        add_mp2_variants(system_name, l, energies)

                except FileFormatError as e:
                    LOG.warn('Invalid G09 log file %s: %s', f, e)
            else:
                LOG.warn('Ignoring %s as SCF did not converge', f)
            pbar.update(f.stat().st_size)

    return energies


def get_required_geometries(benchmark_info, *, suffix='.xyz'):
    required_geometries = set()
    for r in benchmark_info['reactions'].values():
        required_geometries = required_geometries.union(
                set(r['reactants'][1] + r['products'][1]))
    required_geometries = set(rsuffix(s, suffix) for s in required_geometries)
    return required_geometries




def generate_inputs():
    """ Given a directory with an info.json file and N .xyz files,
    create a subdirectory for each method and generate g09 input files
    for each system required in the reactions specified in info.json

    """
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

    parser.add_argument('--progress', default=False,
                        help='Show progress bars')
    args = parser.parse_args()

    logging.basicConfig(format=LOG_FORMAT, level=args.log_level)
    info_file = Path(args.directory, 'info.json')
    LOG.debug('Reading benchmark file from %s', info_file)
    benchmark_info = read_benchmark_info(str(info_file))
    required_geometries = get_required_geometries(benchmark_info, suffix=args.file_suffix)
    LOG.info('%d geometry files required for all reactions', len(required_geometries))
    LOG.debug("Required geometries: %s", required_geometries)

    systems = read_systems(Path(args.directory),
                           required_geometries,
                           prefix=benchmark_info['benchmark'],
                           suffix=args.file_suffix,
                           progress=args.progress)
    LOG.debug('Systems: %s', systems)
    reactions = read_reactions(benchmark_info['reactions'], systems, prefix=benchmark_info['benchmark'], suffix=args.file_suffix)
    skipped = create_input_files(args.directory, systems, args.basis_set, progress=args.progress)
    benchmark_info['post process'] = skipped
    write_benchmark_info(str(info_file), benchmark_info)


def process_outputs(directory, output_directory, progress=False, overwrite=False):
    info_file = Path(directory, 'info.json')
    if not overwrite:
        if Path(directory, 'reaction_energies.json').exists():
            LOG.info('Skipping %s, already processed', directory)
            return

    benchmark_info = read_benchmark_info(info_file)
    benchmark_name = benchmark_info['benchmark']
    required_geometries = get_required_geometries(benchmark_info)
    copy_to = None

    if output_directory is not None:
        Path(output_directory).mkdir()
        shutil.copy(info_file, Path(output_directory, 'info.json'))
        copy_to = Path(output_directory, 'xyz')
        copy_to.mkdir()
    else:
        output_directory = directory

    systems = read_systems(Path(directory),
                           required_geometries,
                           prefix=benchmark_info['benchmark'],
                           copy_to=copy_to,
                           progress=progress)


    subdirs = [p for p in Path(directory, 'calcs').iterdir() if p.is_dir()]
    t1 = time.time()
    size_counter = 0
    suffix = '.log'
    for d in tqdm(subdirs, desc='Calculating size', disable=(not progress)):
        for f in d.iterdir():
            if f.name.endswith(suffix):
                size_counter += f.stat().st_size

    with tqdm(total=size_counter, desc='Reading energies', unit='B', unit_scale=True,
              disable=(not progress)) as pbar:
        energies = read_outputs(subdirs, systems, pbar, expected=len(required_geometries))
    t2 = time.time()
    LOG.debug('%s energies in %s s', len(energies) * len(systems), (t2-t1))
    write_benchmark_info(Path(output_directory, 'energies.json'),
                         energies)
    reactions = read_reactions(benchmark_info['reactions'],
                               systems, prefix=benchmark_info['benchmark'])

    reaction_energies = defaultdict(dict)
    for reaction, stoich in reactions.items():
        for method_name, sp_energies in energies.items():
            try:
                reaction_energies[reaction][method_name] = \
                        sum(sp_energies[s] * n for s, n in stoich)
                LOG.debug('Energy for %s/%s: %d', reaction, method_name, reaction_energies[reaction][method_name])
            except KeyError as e:
                LOG.debug('Missing single point energy method=%s, system=%s', method_name, e)

    write_benchmark_info(Path(output_directory, 'reaction_energies.json'),
                         reaction_energies)


def process_outputs_main():
    """ Main method to process output files from g09 calculations
    Assumes directory structure is as the output from generate_inputs would
    leave.

    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', default='.', 
                        help='Path in which to look for input')
    parser.add_argument('-s', '--file-suffix', default='.log',
                        help="Suffix when looking for output files")
    parser.add_argument('--log-level', default='WARN',
                        help='Level of log info to display')
    parser.add_argument('--d3-correction', default='d3bj',
                        help='Perform Grimme D3 correction for dft functionals')
    parser.add_argument('--output-directory', '-o', default=None,
                        help='Location to place resulting/output files')
    parser.add_argument('--progress', default=False,
                        help='Show progress bars')
    args = parser.parse_args()

    # set the output directory to default if not set

    logging.basicConfig(format=LOG_FORMAT, level=args.log_level)

    process_outputs(args.directory, args.output_directory, progress=args.progress)


def process_outputs_batch():
    """ Main method to process output files from g09 calculations
    Assumes directory structure is as the output from generate_inputs would
    leave.

    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', default='.', 
                        help='Path in which to look for input')
    parser.add_argument('-s', '--file-suffix', default='.log',
                        help="Suffix when looking for output files")
    parser.add_argument('--log-level', default='WARN',
                        help='Level of log info to display')
    parser.add_argument('--d3-correction', default='d3bj',
                        help='Perform Grimme D3 correction for dft functionals')
    parser.add_argument('--log-to', default=None,
                        help='Log to a file')
    parser.add_argument('--progress', default=False,
                        help='Show progress bars')
    parser.add_argument('--overwrite', default=False,
                        help='Overwrite previous processing results')
    args = parser.parse_args()

    # set the output directory to default if not set

    logging.basicConfig(filename=args.log_to, format=LOG_FORMAT, level=args.log_level)

    for directory in tqdm(list(Path(args.directory).iterdir()),
                          desc='Benchmark directories',
                          unit='dir', disable=(not args.progress)):
        if directory.is_dir():
            process_outputs(directory, None, progress=args.progress, overwrite=args.overwrite)
