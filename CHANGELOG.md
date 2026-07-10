# Changelog

All notable changes to this project are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## v0.4.0 - 2026-07-10

### Added

- **HuggingFace Buckets support** — catalogs can now be stored in a HF Bucket
  (`hf://buckets/org/name`), an S3-like storage backend with no git history or
  LFS. Uses `batch_bucket_files()` for writes and `download_bucket_files()` for
  reads. See [docs/buckets.qmd](docs/buckets.qmd).
- `docs/buckets.qmd` — new documentation page for the Buckets backend, linked
  from the site nav, README, and the architecture/local-catalog docs.
- Expanded `README.md` with a full CLI command reference, a `faceberg.yml`
  config example, Local Catalogs/Buckets sections, a Python API method table,
  and a `just`-based development workflow, plus a note that the project is
  alpha-quality software.

### Fixed

- `faceberg <catalog> sync <table>` ignored the `<table>` argument and always
  resynced every dataset in the catalog; it now syncs only the requested
  table.
- Quickstart SQL examples in `README.md` and `docs/*.qmd` referenced the
  `iceberg_catalog` alias, but `faceberg quack`/`serve` actually attach the
  catalog as `faceberg`, so the copy-pasted queries failed. Also documented
  the previously-undocumented `info`/`remove` commands and removed a
  nonexistent REST create-table endpoint and dead `ARCHITECTURE.md` link from
  the docs.
- `faceberg --version` reported a hardcoded `0.1.0` instead of the installed
  package version; it now reads from the generated `_version.py`.
- Cross-links to the DuckDB/Pandas integration docs pointed at a nonexistent
  `integrations/` subdirectory (both in `docs/*.qmd` and in `README.md`); they
  now point at the correct top-level pages.
- `pyproject.toml`'s `requires-python = ">=3.9"` combined with
  `huggingface_hub>=1.10.0` made `uv sync` unsatisfiable, since
  `huggingface_hub>=1.16.4` dropped Python 3.9 support and 1.16.1–1.16.3 are
  yanked. Bumped `requires-python` to `>=3.10` and raised dependency floors to
  versions verified against the current test suite (pyiceberg 0.11.1,
  huggingface_hub 1.22.0, pyarrow 24.0.0, datasets 5.0.0, fsspec 2026.4.0).
- `pyproject.toml`'s `testpaths = ["tests"]` pointed at a nonexistent
  directory; tests live in `faceberg/tests/`.
- `faceberg <path> init` failed on a local catalog path that didn't exist yet
  (e.g. the README's own `faceberg ./mycatalog init`) — `catalog()` decided
  local vs. remote via `Path(uri).is_dir()`, which is `False` for a
  not-yet-created directory, so it fell through to the "assume HF repo id"
  branch and crashed with a confusing `HFValidationError`. It now also
  recognizes path-like prefixes (`./`, `../`, `/`, `~/`).
- The README's raw DuckDB `ATTACH` example was missing the `ENDPOINT` option
  required by the current duckdb iceberg extension; copy-pasting it verbatim
  failed.

## v0.3.0 and earlier

Initial alpha development: dataset discovery from HF Datasets/Parquet exports,
Iceberg metadata generation, local and remote (HF Spaces/Datasets) catalogs,
CLI (`init`/`add`/`sync`/`scan`/`serve`/`quack`), REST catalog server, DuckDB
WASM web UI, and Quarto-based documentation site. See `git log` for full detail.
