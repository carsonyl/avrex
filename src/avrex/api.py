import os
from collections import OrderedDict
from datetime import date
from typing import Union
from urllib.parse import urlparse, parse_qs, urljoin

import bs4
import mechanicalsoup
from mechanicalsoup import LinkNotFoundError


class LoginError(Exception):
    def __init__(self, msg):
        super(LoginError, self).__init__(msg)


def _get_options_map(options: list[bs4.element.Tag]) -> OrderedDict:
    """
    Given a list of `<option>` tags, return a mapping of option value to label.
    Empty options or options with value of "0" are excluded.
    """
    mapping = OrderedDict()
    for option in options:
        value, label = option["value"], option.string
        if not value or value == "0" or not label:
            continue
        mapping[value] = label
    return mapping


class LenientDict(dict):
    """
    All keys are cast to lowercase strings.
    """

    def __getitem__(self, k):
        return super().__getitem__(str(k).lower())

    def __setitem__(self, k, v):
        super().__setitem__(str(k).lower(), v)


def _get_lenient_choices(options_map: dict, extra_aliases: dict = None):
    """
    Returns `options_map` as a one-to-one map. Numeric values are mapped as both str and int keys.

    :param options_map: Mapping of option label to value.
    :param extra_aliases: Aliases to add. Mapping of alias to anything in the one-to-one map.
    :raises KeyError: If a value of `extra_aliases` doesn't match any existing key.
    """
    choices = LenientDict()
    for key, label in options_map.items():
        choices[key] = key
        choices[label] = key
    if extra_aliases:
        for alias, existing_key in extra_aliases.items():
            choices[alias] = choices[existing_key]
    return choices


EXTRA_FORMAT_MAPPINGS = {
    "CSV": "Comma Delimited",
    "PSV": "Pipe Delimited",
    "TSV": "Tab Delimited",
}


class AssociationVoiceApi:
    def __init__(self, username=None, password=None, login_url=None):
        username = username or os.environ.get("AV_USERNAME")
        password = password or os.environ.get("AV_PASSWORD")
        login_url = login_url or os.environ.get("AV_URL")
        if not all((username, password, login_url)):
            raise ValueError(
                "Arguments must be specified, or environment variables AV_USERNAME, AV_PASSWORD, AV_URL must be set"
            )

        browser = mechanicalsoup.StatefulBrowser(raise_on_404=True)
        browser.open(login_url)
        try:
            browser.select_form("#form1")
        except LinkNotFoundError as e:
            raise LoginError(f"Login form not found on {browser.url}") from e

        browser["user_name"] = username
        browser["password"] = password
        browser.submit_selected()

        error = browser.page.find("div", class_="clsError")
        if error:
            raise LoginError(" ".join(error.stripped_strings))

        refresh_content = browser.page.select("meta[http-equiv='refresh']")[0]["content"]
        location = refresh_content[refresh_content.find("url=") + len("url=") :].strip()
        browser.open(location)

        assn_id = parse_qs(urlparse(location).query)["assn_id"][0]

        self._reports_url = urljoin(browser.url, "/Reports/" + assn_id)
        self.browser = browser

    def list_reports(self) -> OrderedDict:
        """
        List available reports from the site.

        :return: Keys are report IDs, values are report labels.
        """
        self.browser.open(self._reports_url)
        return _get_options_map(self.browser.page.select("#report_id option"))

    def download_report(
        self,
        report_name_or_id,
        from_date: Union[None, str, date],
        to_date: Union[None, str, date],
        format_name_or_id,
        out_file,
    ):
        """
        Download a report.

        :param report_name_or_id: For instance "3", or "Site Users".
        :param from_date: If applicable to the report.
        :param to_date: If applicable to the report.
        :param format_name_or_id: For instance "4", or "Comma Delimited", or "CSV".
        :param out_file: Destination file handle in 'wb' mode.
        """
        browser = self.browser
        browser.open(self._reports_url)
        report_choices = _get_lenient_choices(_get_options_map(self.browser.page.select("#report_id option")))
        format_choices = _get_lenient_choices(
            _get_options_map(self.browser.page.select("#format_id option")), EXTRA_FORMAT_MAPPINGS
        )

        browser.select_form("#form1")
        browser["report_id"] = report_choices[report_name_or_id]
        if from_date:
            browser["start_date"] = from_date
        if to_date:
            browser["end_date"] = to_date
        browser["format_id"] = format_choices[format_name_or_id]

        browser.form.form.attrs["action"] = browser.form.form.attrs["action"].strip()
        with browser.submit_selected(update_state=False, stream=True) as resp:
            resp.raise_for_status()
            for chunk in resp.iter_content(chunk_size=None):
                if not chunk:
                    continue
                out_file.write(chunk)
