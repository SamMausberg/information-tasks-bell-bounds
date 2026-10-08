#!/usr/bin/env python3
"""Reproduce the published v2 Latin Modern formatting of one citation line.

The complete manuscript is compiled from LaTeX first. This step changes only
the font/spacing of the already-correct reference [13] line; it never reads the
published PDF. Latin Modern is located in the installed TeX distribution.
"""
from pathlib import Path
import hashlib
import math
import subprocess
import sys

import pymupdf

LINE = 'Tomasz Tylec. Bell measurement ruling out'
REGION = pymupdf.Rect(78.3, 677.7, 288.4, 689.8)
FONT_SHA256 = '1aa18cfefa58132c52ce5de70db1fd1154201c19cd2b2cdaffba4906a33e6852'


def normalized(text):
    return ' '.join(text.split())


def outside_region(pixmap):
    data = bytearray(pixmap.samples)
    # Exclude only the known formatting rectangle, allowing antialiasing at its edge.
    x0, y0 = math.floor(REGION.x0 * 2) - 2, math.floor(REGION.y0 * 2) - 2
    x1, y1 = math.ceil(REGION.x1 * 2) + 2, math.ceil(REGION.y1 * 2) + 2
    for y in range(y0, y1):
        start, stop = (y * pixmap.width + x0) * 3, (y * pixmap.width + x1) * 3
        data[start:stop] = b'\xff' * (stop - start)
    return data


def main():
    if len(sys.argv) != 3:
        raise SystemExit('Usage: format_reference.py COMPILED.pdf OUTPUT.pdf')
    source_path, output_path = map(Path, sys.argv[1:])
    if source_path.resolve() == output_path.resolve():
        raise SystemExit('Input and output must be different files.')
    font_path = Path(subprocess.check_output(
        ['kpsewhich', 'lmroman10-regular.otf'], text=True).strip())
    if not font_path.is_file() or hashlib.sha256(font_path.read_bytes()).hexdigest() != FONT_SHA256:
        raise SystemExit('The reference Latin Modern Roman 10 font is required.')
    source = pymupdf.open(source_path)
    if len(source) != 18:
        raise SystemExit('Expected the published 18-page manuscript.')
    targets = []
    for page_index, page in enumerate(source):
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines', []):
                text = ''.join(span['text'] for span in line['spans'])
                if normalized(text) == LINE:
                    targets.append((page_index, pymupdf.Rect(line['bbox'])))
    if len(targets) != 1 or targets[0][0] != 11 or not REGION.contains(targets[0][1]):
        raise SystemExit(f'The unique reference [13] line is not in its expected position: {targets}')
    page = source[11]
    page.add_redact_annot(REGION, fill=(1, 1, 1))
    page.apply_redactions(images=0, graphics=0)
    page.insert_font(fontname='CitationRoman', fontfile=str(font_path))
    page.insert_text((78.633995, 686.806274), LINE, fontname='CitationRoman',
                     fontsize=10.90909958, color=(0, 0, 0))
    source.save(output_path, garbage=4, deflate=True)
    source.close()
    before, after = pymupdf.open(source_path), pymupdf.open(output_path)
    for index in range(18):
        if normalized(before[index].get_text(sort=True)) != normalized(after[index].get_text(sort=True)):
            raise SystemExit(f'Formatting changed text on page {index + 1}.')
        first = before[index].get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
        second = after[index].get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
        equal = (outside_region(first) == outside_region(second)) if index == 11 else (first.samples == second.samples)
        if not equal:
            raise SystemExit(f'Formatting changed pixels outside the citation line on page {index + 1}.')
    print('PASS: reference [13] publication formatting restored; text and all other pixels unchanged.')


if __name__ == '__main__':
    main()
