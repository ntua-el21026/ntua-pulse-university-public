#!/usr/bin/env python3
"""Build a separate Pulse University report preview from the retained source."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory

FIGURES = (
    'Q04_plan1.png', 'Q04_plan2.png', 'Q04_joins.png',
    'Q06_plan1.png', 'Q06_plan2.png', 'Q06_joins.png',
)

def replace_once(text, original, replacement):
    if text.count(original) != 1:
        raise ValueError(f'Unexpected report source near {original!r}')
    return text.replace(original, replacement, 1)

def preview(source):
    text = source.read_text(encoding='utf-8')
    text = replace_once(text, r'\newfontfamily\greekfonttt{FreeMono}', r'\newfontfamily\greekfonttt{DejaVu Sans Mono}')
    text = replace_once(text, r'\setmainfont{Linux Libertine O}', r'\setmainfont{DejaVu Serif}')
    text = replace_once(
        text,
        r'\includegraphics[width=0.4\textwidth]{emp_logo.png}',
        r'\parbox{0.74\textwidth}{\centering\textit{Source preview. The original cover emblem and six query-plan figures are absent. The archived report preserves their appearances.}}',
    )
    for figure in FIGURES:
        marker = r'\includegraphics[width=\linewidth]{' + figure + '}'
        placeholder = r'\fbox{\parbox{0.88\linewidth}{\centering\textit{Original query-plan figure unavailable in this source preview.}\\[0.2cm]\texttt{\detokenize{'+figure+r'}}}}'
        text = replace_once(text, marker, placeholder)
    return text

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='new PDF path outside the repository')
    parser.add_argument('--repository', type=Path, default=Path(__file__).resolve().parents[1], help='path to the project checkout')
    args=parser.parse_args()
    repo=args.repository.resolve(strict=True)
    output=args.output.absolute()
    if output.suffix.lower() != '.pdf' or output.resolve().is_relative_to(repo):
        parser.error('choose a new .pdf destination outside the repository')
    if output.exists() or output.is_symlink():
        parser.error('the output already exists')
    with TemporaryDirectory(prefix='pulse-source-preview-') as tmp:
        build=Path(tmp)
        docs=build/'docs'
        docs.mkdir()
        shutil.copytree(repo/'diagrams',build/'diagrams')
        shutil.copytree(repo/'frontend/public/frontend_images',build/'frontend/public/frontend_images')
        tex=docs/'source-preview.tex'
        tex.write_text(preview(repo/'docs/main.tex'),encoding='utf-8')
        environment=dict(os.environ)
        environment['TEXINPUTS']=os.pathsep.join((str(build/'diagrams'),str(build/'frontend/public/frontend_images'),''))
        for _ in range(2):
            result=subprocess.run(['xelatex','-no-shell-escape','-halt-on-error','-interaction=nonstopmode',tex.name],
                                  cwd=docs,env=environment,check=False,capture_output=True,text=True)
            if result.returncode:
                raise SystemExit(result.stdout.splitlines()[-35:])
        with output.open('xb') as result:
            result.write(tex.with_suffix('.pdf').read_bytes())
    print(f'Wrote source preview: {output}')

if __name__=='__main__':
    main()
