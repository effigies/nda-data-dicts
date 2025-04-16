# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "aiofiles",
#     "httpx",
#     "rich",
#     "stamina",
#     "structlog",
# ]
# ///

import asyncio
import json
from typing import Any, Callable

import aiofiles
import httpx
import stamina
from rich.progress import Progress, TextColumn, BarColumn, TimeRemainingColumn


API = "https://nda.nih.gov/api/datadictionary"

MAX_CONCURRENT_REQUESTS = 50
TIMEOUT = httpx.Timeout(
    5.0,  # default
    connect=10.0,
    read=15.0,
)


def retry_only_on_server_errors(exc: Exception) -> bool:
    """Retry only on server errors (5xx), not on client errors (4xx)"""
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code >= 500

    # Retry on connection errors and other httpx errors
    return isinstance(exc, httpx.HTTPError)


@stamina.retry(on=retry_only_on_server_errors, attempts=3)
async def get(client: httpx.AsyncClient, endpoint: str) -> httpx.Response:
    response = await client.get(endpoint)
    response.raise_for_status()

    return response


async def save_dictionary(
    client: httpx.AsyncClient,
    name: str,
    semaphore: asyncio.Semaphore,
    get_callback: Callable[[str], None],
    write_callback: Callable[[str], None],
) -> None:
    async with semaphore:
        get_callback(name)
        response = await get(client, f"/datastructure/{name}/csv")

    async with aiofiles.open(f"csv/{name}.csv", "wb") as f:
        await f.write(response.content)
        write_callback(name)


def summarize(name: str, n: int) -> str:
    if len(name) <= n:
        return name
    start = n // 2 - 1
    return f"{name[:start]}[]{name[-start:]}"


async def main() -> None:
    client = httpx.AsyncClient(
        base_url=API,
        transport=httpx.AsyncHTTPTransport(retries=1),
        timeout=TIMEOUT,
    )
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async with client:
        response = await get(client, "/datastructure")
        datastructures: list[dict[str, Any]] = response.json()

        with open("datastructures.json", "w") as text_file:
            json.dump(datastructures, text_file, indent=2)

        with Progress(
            TextColumn(
                "[progress.description]{task.description} {task.fields[struct]:10s}"
            ),
            BarColumn(),
            TimeRemainingColumn(),
        ) as progress:
            g_task = progress.add_task(
                "Fetching", total=len(datastructures), struct="..."
            )
            w_task = progress.add_task(
                "Writing ", total=len(datastructures), struct="..."
            )

            def get_callback(struct) -> None:
                progress.update(g_task, advance=1, struct=summarize(struct, 10))

            def write_callback(struct) -> None:
                progress.update(w_task, advance=1, struct=summarize(struct, 10))

            tasks = [
                save_dictionary(
                    client,
                    structure["shortName"],
                    semaphore,
                    get_callback,
                    write_callback,
                )
                for structure in datastructures
            ]

            await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
