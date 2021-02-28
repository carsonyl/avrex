# avrex: AssociationVoice reports exporter

[![PyPI](https://img.shields.io/pypi/v/avrex.svg?maxAge=2592000)](https://pypi.org/project/avrex)
[![tests](https://github.com/carsonyl/avrex/actions/workflows/tests.yml/badge.svg)](https://github.com/carsonyl/avrex/actions/workflows/tests.yml)

avrex is a Python library and command-line tool for downloading reports
off websites hosted by [AssociationVoice](https://associationvoice.com/).
AssociationVoice provides websites for property management, and may be used
by groups like strata corporations, condo boards, and homeowner associations (HOAs).

avrex makes it easy for data stored on AssociationVoice websites to be
exported for backup, automation, analysis, and transformation.

## Installation

`pip install avrex`

Supports Python 3.7+. Tested on Python 3.9.

## Usage

For all operations, avrex needs the URL for the AssociationVoice site's login page,
and a corresponding username and password.
These arguments are automatically picked up from the environment variables
`AV_URL`, `AV_USERNAME`, and `AV_PASSWORD`.
They are also automatically loaded from an Envfile if present,
and accepted as options in the CLI, and as arguments in the API.

### Command-line interface

Installation adds the `avrex` script. The commands are `avrex reports` and `avrex download-report`:

```
> avrex reports --help
Usage: avrex reports [OPTIONS]

  List available reports.

Options:
  --username TEXT
  --password TEXT
  --url TEXT       URL to login page
  --help           Show this message and exit.

```

```
> avrex download-report --help
Usage: avrex download-report [OPTIONS] REPORT DESTINATION

  Download a report.

  REPORT is a report ID or exact name of a report. DESTINATION is a path to
  a file. Existing files are overwritten. The file must have an extension
  matching a valid export format for the report.

Options:
  --date-range TEXT  Format: YYYY-MM-DD,YYYY-MM-DD
  --username TEXT
  --password TEXT
  --url TEXT         URL to login page
  --help             Show this message and exit.
```

### API

Reports listing and downloading is available in `avrex.AssociationVoiceApi`:

```pycon
>>> from avrex import AssociationVoiceApi
>>> api = AssociationVoiceApi(username="foo", password="bar", url="https://secure.associationvoice.com/Account/Login/100")
>>> api.list_reports()
OrderedDict([('16', 'Advanced Map Usage'), ('6', 'Directory - Communication Methods Updates'), ('15', ...
>>> with open("comm-updates.csv", "wb") as outf:
...    api.download_report("Directory - Communication Methods Updates", "2021-01-01", "2021-01-31", "CSV", outf)

```