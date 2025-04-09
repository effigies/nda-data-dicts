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
from functools import cache

import httpx
import stamina
from rich.progress import track


API = "https://nda.nih.gov/api/datadictionary"

@cache
def get_client(url: str) -> httpx.Client:
    return httpx.Client(base_url=url)


@stamina.retry(on=httpx.HTTPError)
def get(api: str, endpoint: str) -> httpx.Response:
    response = get_client(api).get(endpoint)
    response.raise_for_status()

    return response


def get_datastructures(api: str) -> dict:
    response = get(api, "/datastructure")
    return response.json()


def get_dictionary(api: str, shortname: str) -> bytes:
    response = get(api, f"/datastructure/{shortname}/csv")
    return response.content


if __name__ == "__main__":
    datastructures = get_datastructures(API)

    with open("datastructures.json", "w") as f:
        json.dump(datastructures, f, indent=2)

    for structure in track(datastructures):
        shortname = structure["shortName"]

        csv_data = get_dictionary(API, shortname)
        with open(f"{shortname}.csv", "wb") as f:
            f.write(csv_data)
