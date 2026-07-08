![Faceberg](https://github.com/kszucs/faceberg/blob/main/faceberg.png?raw=true)

# Faceberg

**Bridge HuggingFace datasets with Apache Iceberg tables — no data copying, just metadata.**

Faceberg maps HuggingFace datasets to Apache Iceberg tables. Your catalog metadata lives on HuggingFace Spaces (or Buckets) with an auto-deployed REST API, and any Iceberg-compatible query engine can access the data.

> [!NOTE]
> Faceberg is early-stage, alpha-quality software — APIs and CLI flags may still evolve between releases. See [CHANGELOG.md](CHANGELOG.md) for what's landed so far.

## Installation

```bash
pip install faceberg
```

Requires Python 3.10+. The REST catalog server (`faceberg serve`) is included by default.

## Prerequisites

Get a token from [HuggingFace Settings](https://huggingface.co/settings/tokens) and export it:

```bash
export HF_TOKEN=your_huggingface_token
```

The token is only required for remote catalogs (`user/repo`, `hf://...`). Local catalogs (plain paths) don't need one.

## Quick Start

```bash
# Create a catalog on HuggingFace Hub (deploys a Space with a REST API)
faceberg user/mycatalog init

# Add datasets — table identifier is inferred (org.repo) unless --table is given
faceberg user/mycatalog add stanfordnlp/imdb
faceberg user/mycatalog add openai/gsm8k --config main

# List what's in the catalog
faceberg user/mycatalog list

# Query with interactive DuckDB shell
faceberg user/mycatalog quack
```

```sql
SELECT label, substr(text, 1, 100) as preview
FROM faceberg.stanfordnlp.imdb
LIMIT 10;
```

## CLI Reference

Every command follows the same shape: `faceberg <catalog-uri> <command> [args]`, where `<catalog-uri>` is one of:

| URI form | Backend |
|---|---|
| `org/repo` or `hf://datasets/org/repo` | HuggingFace dataset repo (Space auto-deployed) |
| `hf://spaces/org/repo` | HuggingFace Space |
| `hf://buckets/org/repo` | HuggingFace Bucket (S3-like, no git history) |
| `./path` or `/abs/path` | Local filesystem catalog |

| Command | Description |
|---|---|
| `init [config.yml]` | Create the catalog. Auto-discovers `./faceberg.yml` if no path is given; `--sync` populates tables immediately. |
| `add <dataset>` | Add a HuggingFace dataset as a table. `--table ns.table` sets an explicit identifier, `--config` selects a dataset config. |
| `sync [table]` | Re-check datasets for new revisions and update Iceberg metadata. Omit `table` to sync everything; `--tree-view` shows progress as a tree. |
| `list` | List all namespaces/tables in the catalog. |
| `info <table>` | Show a table's schema, partitioning, and metadata location. |
| `scan <table>` | Read and print sample rows. `--limit/-n` controls row count (default 5). |
| `remove <identifier>` | Drop a table (`ns.table`) or an empty namespace. `--yes` skips the confirmation prompt. |
| `serve` | Start an Iceberg REST catalog server. `--host`, `--port` (default 8181), `--reload`, `--prefix`. |
| `quack` | Open an interactive DuckDB shell with the catalog pre-attached. `--endpoint` overrides auto-detection. |

Run `faceberg <uri> <command> --help` for full flag details and examples on any command.

## `faceberg.yml`

Catalogs are described by a `faceberg.yml` config that tracks dataset-to-table mappings:

```yaml
default:
  imdb:
    type: dataset
    repo: stanfordnlp/imdb
    config: plain_text
  gsm8k:
    type: dataset
    repo: openai/gsm8k
    config: main
```

`faceberg init tables.yml` bootstraps a catalog from a file like this in one shot; `faceberg sync` re-reads it and updates any table whose source dataset revision changed.

## Local Catalogs

For development, testing, or CI, point the CLI at a filesystem path instead of a HuggingFace URI — no token needed:

```bash
faceberg ./mycatalog init
faceberg ./mycatalog add stanfordnlp/imdb --config plain_text
faceberg ./mycatalog serve --port 8181   # in one terminal
faceberg ./mycatalog quack               # in another
```

See [Local Catalogs](https://faceberg.kszucs.dev/local.html) for the on-disk layout and testing patterns.

## HuggingFace Buckets

Catalog metadata can also live in a [HuggingFace Bucket](https://faceberg.kszucs.dev/buckets.html) (`hf://buckets/org/name`) instead of a Space — an S3-like storage backend with no git history, useful for catalogs that don't need a hosted REST endpoint:

```bash
faceberg hf://buckets/user/mycatalog init
faceberg hf://buckets/user/mycatalog add stanfordnlp/imdb
```

## How It Works

```
HuggingFace Hub
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ┌─────────────────────┐    ┌─────────────────────────┐ │
│  │  HF Datasets        │    │  HF Spaces (Catalog)    │ │
│  │  (Original Parquet) │◄───│  • Iceberg metadata     │ │
│  │                     │    │  • REST API endpoint    │ │
│  │  stanfordnlp/imdb/  │    │  • faceberg.yml         │ │
│  │   └── *.parquet     │    │                         │ │
│  └─────────────────────┘    └───────────┬─────────────┘ │
│                                         │               │
└─────────────────────────────────────────┼───────────────┘
                                          │ Iceberg REST API
                                          ▼
                              ┌─────────────────────────┐
                              │     Query Engines       │
                              │  DuckDB, Pandas, Spark  │
                              └─────────────────────────┘
```

**No data is copied** — only metadata is created. Query with DuckDB, PyIceberg, Spark, or any Iceberg-compatible tool.

## Python API

```python
import os
from faceberg import catalog

cat = catalog("user/mycatalog", hf_token=os.environ.get("HF_TOKEN"))
table = cat.load_table("stanfordnlp.imdb")
df = table.scan(limit=100).to_pandas()
```

The catalog object exposes the usual Iceberg operations:

| Method | Description |
|---|---|
| `init(config)` | Initialize catalog storage, optionally with a `Config` |
| `config()` | Load the catalog's `faceberg.yml` configuration |
| `add_dataset(identifier, repo, config)` | Add a HuggingFace dataset as an Iceberg table |
| `sync_dataset(identifier)` / `sync_datasets()` | Sync one or all datasets (update if source changed) |
| `load_table(identifier)` | Load a table for querying |
| `list_tables(namespace)` / `list_namespaces()` | Enumerate tables / namespaces |
| `drop_table(identifier)` / `drop_namespace(identifier)` | Remove a table or empty namespace |
| `table_exists(identifier)` | Check if a table exists |

### Pandas integration

```python
import pandas as pd

df = pd.read_iceberg(
    table_identifier="stanfordnlp.imdb",
    catalog_name="faceberg",
    catalog_properties={"type": "rest", "uri": "https://user-mycatalog.hf.space"},
    columns=["text", "label"],
    limit=10,
)
```

See [Pandas Integration](https://faceberg.kszucs.dev/pandas.html) for the local-catalog variant and more examples.

## Share Your Catalog

Your catalog is accessible to anyone via the REST API:

```python
import duckdb

conn = duckdb.connect()
conn.execute("INSTALL iceberg; LOAD iceberg")
conn.execute("ATTACH 'https://user-mycatalog.hf.space' AS cat (TYPE ICEBERG)")

result = conn.execute("SELECT * FROM cat.stanfordnlp.imdb LIMIT 5").fetchdf()
```

To make your catalog private, set the underlying HuggingFace Space/dataset/Bucket to private.

## Documentation

**[Read the docs →](https://faceberg.kszucs.dev/)**

- [Getting Started](https://faceberg.kszucs.dev/) — Full quickstart guide
- [Local Catalogs](https://faceberg.kszucs.dev/local.html) — Use local catalogs for development
- [Buckets](https://faceberg.kszucs.dev/buckets.html) — Store catalog metadata in HF Buckets
- [DuckDB Integration](https://faceberg.kszucs.dev/duckdb.html) — Advanced SQL queries
- [Pandas Integration](https://faceberg.kszucs.dev/pandas.html) — Load into DataFrames
- [Architecture](https://faceberg.kszucs.dev/design.html) — How Faceberg maps datasets to Iceberg metadata

## Development

```bash
git clone https://github.com/kszucs/faceberg
cd faceberg
pip install -e '.[dev]'
```

Common tasks are wired up via `just` (see the [justfile](justfile)):

```bash
just test     # run the test suite (pytest faceberg/tests/)
just cov      # run tests with coverage
just format   # format code with ruff
just check    # lint + format check
just build    # build distribution packages
```

Docs are written in Quarto (`docs/*.qmd`) and published to https://faceberg.kszucs.dev/.

## License

Apache 2.0
