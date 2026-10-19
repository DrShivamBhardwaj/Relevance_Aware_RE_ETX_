"""Check package integrity; optionally re-audit all archived Cooja runs."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checksum_files():
    checked = 0
    for line in (ROOT / 'SHA256SUMS').read_text().splitlines():
        expected, name = line.split('  ', 1)
        path = (ROOT / name).resolve()
        require(path.is_relative_to(ROOT), f'Unsafe checksum path: {name}')
        require(path.is_file(), f'Missing file: {name}')
        with path.open('rb') as handle:
            actual = hashlib.file_digest(handle, 'sha256').hexdigest()
        require(actual == expected, f'Checksum mismatch: {name}')
        checked += 1
    require(checked > 100, 'Incomplete checksum inventory')
    return checked


def check_outcomes():
    folder = ROOT / 'results/cooja_v2'
    for name, count, seed_cases in [('primary', 200, 20), ('exploratory', 280, 28)]:
        with (folder / f'{name}_seed_results.csv').open(newline='') as handle:
            rows = list(csv.DictReader(handle))
        keys = [(r['case'], r['seed'], r['policy']) for r in rows]
        require(len(rows) == count and len(set(keys)) == count,
                f'Unexpected/duplicate {name} outcomes')
        cases = {(r['case'], r['seed']) for r in rows}
        require(len(cases) == seed_cases, f'Unexpected {name} seed/case count')
        require(all(sum((r['case'], r['seed']) == key for r in rows) == 10
                    for key in cases), f'Incomplete policies in {name}')
    require(len(list((ROOT / 'figures').glob('fig[0-9][0-9].png'))) == 9,
            'Expected nine original figures')
    require(len(list((ROOT / 'tables').glob('table[0-9][0-9].csv'))) == 10,
            'Expected ten numbered tables')


def audit_raw():
    results = ROOT / 'results/cooja_v2'
    with tempfile.TemporaryDirectory(prefix='relevance-verify-') as tmp:
        work = Path(tmp)
        for scope, stem in [('primary', 'primary'), ('exploratory', 'robustness')]:
            with tarfile.open(results / f'{scope}_evidence.tar.xz') as archive:
                archive.extractall(work, filter='data')
            for script, suffix in [('audit_outputs.py', 'audit'), ('analyse.py', 'analysis')]:
                target = work / f'{scope}-{suffix}.json'
                subprocess.run([sys.executable, str(ROOT / 'validation/cooja' / script),
                                str(work / scope), '--output', str(target)], check=True)
                expected = json.loads((results / f'cooja_{stem}_{suffix}.json').read_text())
                require(json.loads(target.read_text()) == expected,
                        f'Regenerated {scope} {suffix} differs from archive')
            print(f'{scope}: independent raw audit and paired analysis match exactly', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', action='store_true', help='re-audit and analyze all 480 raw runs')
    args = parser.parse_args()
    count = checksum_files()
    check_outcomes()
    print(f'{count} file checksums passed; 480 outcomes, 9 figures and 10 tables checked', flush=True)
    if args.raw:
        audit_raw()


if __name__ == '__main__':
    main()
