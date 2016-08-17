def extract_tonto_energy(filename):
    with open(filename) as f:
        for line in f:
            if 'Total energy' in line:
                return float(re.findall('[-+]\d+[\.]?\d*', line)[0])
