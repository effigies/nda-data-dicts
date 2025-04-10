# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx",
#     "rich",
#     "stamina",
#     "structlog",
# ]
# ///

import json
from typing import Any

import httpx
import stamina
from rich.progress import track


API = "https://nda.nih.gov/api/datadictionary"


def retry_only_on_server_errors(exc: Exception) -> bool:
    """Retry only on server errors (5xx), not on client errors (4xx)"""
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code >= 500

    # Retry on connection errors and other httpx errors
    return isinstance(exc, httpx.HTTPError)


@stamina.retry(on=retry_only_on_server_errors, attempts=3)
def get(client: httpx.Client, endpoint: str) -> httpx.Response:
    response = client.get(endpoint)
    response.raise_for_status()

    return response


if __name__ == "__main__":
    client = httpx.Client(base_url=API, transport=httpx.HTTPTransport(retries=1))
    with client:
        datastructures: list[dict[str, Any]] = get(client, "/datastructure").json()

        with open("datastructures.json", "w") as text_file:
            json.dump(datastructures, text_file, indent=2)

        for structure in track(datastructures):
            shortname: str = structure["shortName"]
            data = get(client, f"/datastructure/{shortname}/csv").content

            with open(f"csv/{shortname}.csv", "wb") as bin_file:
                bin_file.write(data)
