from datetime import datetime
from pathlib import Path

import click
from click import BadParameter

from avrex import AssociationVoiceApi


@click.group()
def main():
    pass


@main.command()
@click.option("--username", envvar="AV_USERNAME")
@click.option("--password", envvar="AV_PASSWORD", hide_input=True)
@click.option("--url", envvar="AV_URL", help="URL to login page")
def reports(username, password, url):
    """
    List available reports.
    """
    api = AssociationVoiceApi(username, password, url)
    for report_id, label in api.list_reports().items():
        print(f"{report_id}\t{label}")


def parse_date_range(ctx, param, value):
    if not value:
        return None, None
    try:
        start, end = value.split(",")
        return datetime.fromisoformat(start).date(), datetime.fromisoformat(end).date()
    except ValueError as e:
        raise BadParameter("Date range need to be in format YYYY-MM-DD,YYYY-MM-DD") from e


@main.command()
@click.argument("report")
@click.argument("destination", type=click.File(mode="wb"))
@click.option("--date-range", callback=parse_date_range, help="Format: YYYY-MM-DD,YYYY-MM-DD")
@click.option("--username", envvar="AV_USERNAME")
@click.option("--password", envvar="AV_PASSWORD", hide_input=True)
@click.option("--url", envvar="AV_URL", help="URL to login page")
def download_report(report, destination, date_range, username, password, url):
    """
    Download a report.

    REPORT is a report ID or exact name of a report.
    DESTINATION is a path to a file. Existing files are overwritten.
    The file must have an extension matching a valid export format for the report.
    """
    api = AssociationVoiceApi(username, password, url)
    extension = Path(destination.name).suffix.strip(".")
    if not extension:
        raise ValueError("Destination file must have an extension of a valid export format")
    api.download_report(report, date_range[0], date_range[1], extension, destination)


if __name__ == "__main__":
    main()
