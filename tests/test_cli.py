from datetime import date

import pytest
from click import BadParameter
from click.testing import CliRunner
from avrex.cli import main, parse_date_range


@pytest.mark.live
def test_reports():
    result = CliRunner().invoke(main, ["reports"])
    assert result.exit_code == 0


@pytest.mark.live
def test_download_report(tmp_path):
    dest = str(tmp_path / "foobar.xml")
    result = CliRunner().invoke(
        main,
        ["download-report", "Site Access", dest],
    )
    assert result.exit_code == 0
    with open(dest) as f:
        assert f.read().startswith("<?xml")


def test_parse_date_range():
    start, end = parse_date_range(None, None, "2021-01-01,2021-01-31")
    assert start == date(2021, 1, 1)
    assert end == date(2021, 1, 31)
    with pytest.raises(BadParameter):
        parse_date_range(None, None, "123")
