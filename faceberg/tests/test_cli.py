"""Tests for CLI commands."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from faceberg import config as cfg
from faceberg.cli import main


def test_list_command_with_tree_view(tmp_path):
    """Test list command uses CatalogTreeView for rich display."""
    # Create a local catalog
    catalog_dir = tmp_path / "test_catalog"
    catalog_dir.mkdir()

    # Create config with some tables
    config = cfg.Config()
    config["default"] = cfg.Namespace()
    config["default"]["imdb"] = cfg.Dataset(repo="stanfordnlp/imdb", config="plain_text")
    config["default"]["squad"] = cfg.Dataset(repo="squad", config="plain_text")
    config["analytics"] = cfg.Namespace()
    config["analytics"]["aggregated"] = cfg.Table(uri="")

    # Save config
    config.to_yaml(catalog_dir / "faceberg.yml")

    # Run list command
    runner = CliRunner()
    result = runner.invoke(main, [str(catalog_dir), "list"])

    # Verify command succeeded
    assert result.exit_code == 0

    # Verify output contains catalog name in rich format
    output = result.output

    # Verify namespaces are shown
    assert "default" in output
    assert "analytics" in output

    # Verify dataset nodes are shown with their icons
    assert "imdb" in output
    assert "squad" in output
    assert "aggregated" in output

    # Verify dataset metadata is shown (repo info)
    assert "stanfordnlp/imdb" in output


def test_list_command_empty_catalog(tmp_path):
    """Test list command with empty catalog."""
    catalog_dir = tmp_path / "empty_catalog"
    catalog_dir.mkdir()

    # Create empty config
    config = cfg.Config()
    config.to_yaml(catalog_dir / "faceberg.yml")

    runner = CliRunner()
    result = runner.invoke(main, [str(catalog_dir), "list"])

    # Command should succeed even with empty catalog
    assert result.exit_code == 0


def _fake_catalog():
    """Build a mock catalog with a two-table config, for exercising sync routing."""
    config = cfg.Config()
    config["default"] = cfg.Namespace()
    config["default"]["imdb"] = cfg.Dataset(repo="stanfordnlp/imdb", config="plain_text")
    config["default"]["squad"] = cfg.Dataset(repo="squad", config="plain_text")

    fake_catalog = MagicMock()
    fake_catalog.uri = "fake://catalog"
    fake_catalog.config.return_value = config
    return fake_catalog


def test_sync_command_with_table_name_syncs_only_that_table():
    """Test that `sync <table>` syncs only the named table, not the whole catalog."""
    fake_catalog = _fake_catalog()

    with patch("faceberg.cli.catalog", return_value=fake_catalog):
        runner = CliRunner()
        result = runner.invoke(main, ["fake://catalog", "sync", "default.imdb"])

    assert result.exit_code == 0
    fake_catalog.sync_dataset.assert_called_once()
    assert fake_catalog.sync_dataset.call_args.args[0] == ("default", "imdb")
    fake_catalog.sync_datasets.assert_not_called()


def test_sync_command_without_table_name_syncs_everything():
    """Test that bare `sync` (no table argument) syncs the whole catalog."""
    fake_catalog = _fake_catalog()

    with patch("faceberg.cli.catalog", return_value=fake_catalog):
        runner = CliRunner()
        result = runner.invoke(main, ["fake://catalog", "sync"])

    assert result.exit_code == 0
    fake_catalog.sync_datasets.assert_called_once()
    fake_catalog.sync_dataset.assert_not_called()
