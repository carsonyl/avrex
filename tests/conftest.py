import pytest

from avrex import AssociationVoiceApi


def scrub_response(response):
    """
    Drop irrelevant headers.
    """
    headers = response["headers"]
    for header in [
        "CF-Cache-Status",
        "CF-RAY",
        "Cache-Control",
        "Connection",
        "Date",
        "Expect-CT",
        "NEL",
        "Report-To",
        "Server",
        "Transfer-Encoding",
        "cf-request-id",
        "Set-Cookie",
    ]:
        headers.pop(header, None)
    return response


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "decode_compressed_response": True,
        "filter_query_parameters": list(map(lambda x: (x, "XXXXX"), ["t"])),
        "filter_post_data_parameters": list(map(lambda x: (x, "XXXXX"), ["user_name", "password"])),
        "filter_headers": ["Connection", "Accept-Encoding", "User-Agent", "Cookie"],
        "before_record_response": scrub_response,
    }


@pytest.fixture(scope="module")
def valid_api():
    return AssociationVoiceApi()
