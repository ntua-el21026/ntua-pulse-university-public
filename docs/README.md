# Database design and report evidence

- [Project report](report.pdf) covers the schema, synthetic data generation,
  CLI and UI, and the plan analysis for Q04 and Q06. Its query outputs are
  evidence from the historical run.
- [DDL reference](ddl.pdf) collects the schema, indexes, triggers, stored
  procedures, and views. The [SQL implementation](../sql/README.md) identifies
  the exact source files and installation order.
- [ER and relational diagrams](../diagrams/README.md) record the conceptual
  and relational models.

## Assignment and presentation assets

The NTUA Databases handout defined the festival scenario, query tasks and
course deliverables. It served as a specification and assessment reference.
The team schema, fifteen query implementations, diagrams, recorded
outputs and report are available here. An authorized student can seek the
original 2024–2025 edition through the
[NTUA Databases course](https://www.ece.ntua.gr/en/education/undergraduate/courses?courseId=3123).
The local implementation and recorded outputs can be inspected independently. Exact
replication of the classroom assessment depends on access to that edition.

The historical event photograph supplied background illustration for the
login and logout pages. The application uses an original
[database emblem](../frontend/public/logo.jpg) at the existing path and
retains the two corresponding offline presentation renders
([login](../frontend/public/frontend_images/Login.png),
[logout](../frontend/public/frontend_images/Logout.png)). They use fictional
details. The four other interface captures are historical and remain in
[the screenshot directory](../frontend/public/frontend_images/).
The former photograph, credited to José Fernandes / NOS Alive, is documented through a
[credited publication reference](https://wikinight.eu/pt/musica/cartaz-completo-nos-alive-2025).
Reproducing that historical visual would require authorized access and
appropriate rights from the relevant holder. The application uses the
local emblem for the current demonstration.

## LaTeX source and current PDF

[main.tex](main.tex) retains the submitted report source with the course
link and the two revised capture references. The current
[36-page PDF](report.pdf) was produced through a targeted PDF update:
page 5 uses the official assignment reference, and page 30 contains the two
new screenshot images. A raster comparison matched the other 34 pages
pixel-for-pixel at 72 dpi. This was a PDF-level update to the existing
report.

An exact source rebuild uses XeLaTeX, the packages declared in
[the report source](main.tex), and the FreeMono and Linux Libertine O font
families. It also requires the original cover emblem `emp_logo.png` and
six query-plan figures: `Q04_plan1.png`, `Q04_plan2.png`, `Q04_joins.png`,
`Q06_plan1.png`, `Q06_plan2.png`, and `Q06_joins.png`. These seven files
are external to the repository. The [archived PDF](report.pdf) preserves
their appearances, and the [recorded SQL outputs](../sql/queries/) remain
available for interpreting the plans.

For an exact rebuild, use a separate working copy with the authorized
assets in `docs/`. From that directory, add the retained diagram and
screenshot directories to the XeLaTeX search path. Run the command twice
to resolve references.

```bash
TEXINPUTS="../diagrams:../frontend/public/frontend_images:" \
  xelatex -no-shell-escape -halt-on-error -interaction=nonstopmode main.tex
```

The exact build remains unverified. The local XeLaTeX attempt stopped at
the unavailable FreeMono font before reaching the missing images.

### Build a source preview

The [preview builder](build_report_preview.py) uses Python 3, XeLaTeX,
DejaVu Serif and DejaVu Sans Mono. It compiles a temporary copy with
explicit text markers for the unavailable emblem and figures. It uses the
tracked diagrams and screenshots and leaves the original TeX source and
report PDF intact. Run from the repository root and choose a new output
path outside the checkout.

```bash
python3 docs/build_report_preview.py /path/to/pulse-report-preview.pdf
```

The preview compiled successfully with all seven omission markers. Its
layout and pagination differ from the archived 36-page report, which
remains the reference for the historical submission.

## Historical organization material

[Cardinality notes](organization/cardinality_constraints.txt) document
participation and cardinality assumptions. The
[generated row-count summary](organization/db_data.txt) describes the
synthetic data. The [project tree capture](organization/project_structure.txt)
records an earlier checkout and may show local or generated paths absent from
the current repository. The [root index](../README.md) describes the current layout.
