from click.testing import CliRunner
from avrex.cli import main


def test_reports():
    result = CliRunner().invoke(main, ["reports"])
    assert result.exit_code == 0


def test_download_report(tmp_path):
    dest = str(tmp_path / "foobar.xml")
    result = CliRunner().invoke(
        main,
        ["download-report", "Site Access", dest],
    )
    assert result.exit_code == 0
    with open(dest) as f:
        assert f.read().startswith("<?xml")
