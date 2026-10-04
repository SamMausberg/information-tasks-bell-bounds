#!/usr/bin/env bash
# Build the paper and run the exact finite certificates. No shell escape needed.
set -euo pipefail
cd "$(dirname "$0")"
command -v pdflatex >/dev/null || { echo 'pdflatex is required.' >&2; exit 1; }
command -v python3 >/dev/null || { echo 'Python 3.10 or later is required.' >&2; exit 1; }
mkdir -p build results
python3 scripts/check_certificates.py > results/check_output.txt
for pass in 1 2 3; do
  if ! pdflatex -interaction=nonstopmode -halt-on-error -file-line-error \
       -output-directory=build main.tex > "build/pass-${pass}.txt" 2>&1; then
    cat "build/pass-${pass}.txt" >&2
    exit 1
  fi
done
if grep -E 'LaTeX Warning|Package .* Warning|Overfull|Missing character|^!' build/main.log; then
  echo 'Please inspect the diagnostics printed above.' >&2
  exit 1
fi
cp build/main.pdf paper.pdf
cp build/main.log results/latex_build.log
python3 - <<'PY'
from pathlib import Path
import json, re, subprocess
s = Path('main.tex').read_text(encoding='utf-8')
abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', s, re.S).group(1)
assert len(abstract.split()) < 150, 'The abstract must contain fewer than 150 words.'
checks = json.loads(Path('results/certificates.json').read_text())
log = Path('build/main.log').read_text(errors='replace')
report = {
    'build': 'passed',
    'engine': subprocess.check_output(['pdflatex','--version'],text=True).splitlines()[0],
    'class': 'quantumarticle v6.1 (unmodified class file included)',
    'abstract_word_count': len(abstract.split()),
    'pages': int(re.search(r'Output written on .*?\((\d+) pages',log).group(1)),
    'finite_exact_checks': checks['check_count'],
    'errors_or_unresolved_references': False,
    'overfull_boxes': False,
    'underfull_hbox_diagnostics': len(re.findall(r'Underfull \\hbox',log)),
    'pdf': 'paper.pdf'
}
Path('results/build.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
PY
