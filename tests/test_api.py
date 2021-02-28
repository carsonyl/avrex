import os
from contextlib import contextmanager

import pytest

from avrex import AssociationVoiceApi
from avrex.api import LoginError


@pytest.mark.vcr
def test_login_reject():
    with pytest.raises(LoginError):
        AssociationVoiceApi("foo", "bar", "https://secure.associationvoice.com/Account/Login/100")


@pytest.mark.vcr
def test_login_invalid_url():
    with pytest.raises(LoginError):
        AssociationVoiceApi("foo", "bar", "https://httpbin.org/html")


@contextmanager
def suspend_env(*names):
    suspended = {name: os.environ.pop(name, None) for name in names}
    yield
    for name, value in suspended.items():
        if value is None:
            continue
        os.environ[name] = value


def test_missing_args():
    with suspend_env("AV_USERNAME", "AV_PASSWORD", "AV_URL"):
        with pytest.raises(ValueError):
            AssociationVoiceApi()


@pytest.mark.live
def test_list_reports(valid_api):
    reports = valid_api.list_reports()
    assert reports
    assert "0" not in reports
    for key, value in reports.items():
        assert key
        assert value


@pytest.mark.parametrize(
    "report_id, format_id",
    [
        (9999, 2),  # Invalid report
        (4, 9999),  # Invalid format
        pytest.param(4, 2, marks=pytest.mark.xfail(reason="Only blocked in GUI")),  # Disallowed format for report
    ],
)
@pytest.mark.live
def test_download_report_invalid(valid_api, tmp_path, report_id, format_id):
    with pytest.raises(KeyError):
        valid_api.download_report(report_id, None, None, format_id, tmp_path / "foo.dat")


@pytest.mark.parametrize(
    "report_id, from_date, to_date, format_id",
    [
        (3, None, None, 3),
        (3, None, None, 2),
        (3, "2020-01-01", "2020-02-01", 2),
    ],
)
@pytest.mark.live
def test_download_report(valid_api, tmp_path, report_id, from_date, to_date, format_id):
    with open(tmp_path / "foo.dat", "wb") as outf:
        valid_api.download_report(report_id, from_date, to_date, format_id, outf)
