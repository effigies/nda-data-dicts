# NIMH Data Archive Data Dictionaries

This repository is intended as an archive of the data dictionaries
available at https://nda.nih.gov/general-query.html?q=query=data-structure
([Wayback Machine](https://web.archive.org/web/20250403102229/https://nda.nih.gov/general-query.html?q=query%3Ddata-structure)).

As data dictionaries are added or modified, this dataset will be updated
in order to permit change tracking.

## Contents

* `<repository-root>/`
    * `code/`: Code used to populate the repository
    * `csv/<instrument>.csv`: Data dictionaries, serialized as CSV,
      retrieved from `https://nda.nih.gov/api/datadictionary/<instrument>/csv`
    * `datastructures.json`: Summary data retrieved from `https://nda.nih.gov/api/datadictionary/`

## How to update

With [uv] installed:

```console
uvx datalad run -- uv run code/fetch_dictionaries.py
```

It's a little roundabout, but `uvx` will install [datalad] for you,
which will track the changes to the repository from the command following `--`.
`uv run` will install the code dependencies for you, saving you the trouble
of building an environment.

## License

The code is released under the MIT license.

To the best of my understanding, the data dictionaries are documents in the public domain.

## Notes

We use the HTTP API at https://nda.nih.gov/api/datadictionary/docs/swagger-ui/index.html
([Wayback Machine](https://web.archive.org/web/20250410014947/https://nda.nih.gov/api/datadictionary/docs/v3/api-docs)
of OpenAPI document).
We retrieve a list of all dictionaries and then retrieve each structure as a template.

The initial data snapshot took place on 2025-04-09, totaling ~138MB.
I will aim for at least weekly updates, with empty commits to indicate a successful run with
no changes to the dataset.

This repository is maintained with [git], [git-annex], and [DataLad].
The code utilizes:

* [httpx]: For web requests
* [stamina]: For handling retries
* [rich]: For progress indicators

[git]: https://git-scm.com/
[git-annex]: https://git-annex.branchable.com/
[DataLad]: https://www.datalad.org/
[httpx]: https://www.python-httpx.org/
[stamina]: https://stamina.hynek.me/
[rich]: https://rich.readthedocs.io/
[uv]: https://docs.astral.sh/uv/
