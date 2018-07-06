# conveyor

This project translates the old URL scheme for packages into redirects and serves legacy user documentation.

It's canonical data is pulled from the JSON documents that PyPI serves.

## Tests

### Prerequisites

You'll need `tox` installed and on your path.

```shell
$ pip install --user tox
$ export PATH=$(python -c "import site; import os; print(os.path.join(site.USER_BASE, 'bin'))"):$PATH
```

### Run test suite
```
$ tox
```

## Running

```shell
python3 -m venv .state/venv
.state/venv/bin/pip install -r requirements.txt
export CONVEYOR_ENDPOINT=https://pypi.python.org
export DOCS_BUCKET=pypi-docs
.state/venv/bin/gunicorn -k aiohttp.worker.GunicornWebWorker conveyor.app:application
```

## Deployment

Conveyor reads configuration from the environment:

- `CONVEYOR_ENDPOINT`: The host to query for JSON documents, `https://pypi.python.org`
- `DOCS_BUCKET`: The S3 Bucket that hosts user documentation, `pypi-docs`
