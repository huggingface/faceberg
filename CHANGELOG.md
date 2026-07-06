# Changelog

All notable changes to this project are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unreleased

### Added

- **HuggingFace Buckets support** — catalogs can now be stored in a HF Bucket
  (`hf://buckets/org/name`), an S3-like storage backend with no git history or
  LFS. Uses `batch_bucket_files()` for writes and `download_bucket_files()` for
  reads. See [docs/buckets.qmd](docs/buckets.qmd).
- `docs/buckets.qmd` — new documentation page for the Buckets backend, linked
  from the site nav, README, and the architecture/local-catalog docs.

### Fixed

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

## v0.3.0 and earlier

Initial alpha development: dataset discovery from HF Datasets/Parquet exports,
Iceberg metadata generation, local and remote (HF Spaces/Datasets) catalogs,
CLI (`init`/`add`/`sync`/`scan`/`serve`/`quack`), REST catalog server, DuckDB
WASM web UI, and Quarto-based documentation site. See `git log` for full detail.
