## Django component for the application

Currently, uses django templates, tailwindcss and streaming response to stream SSE
I have django ninja REST API endpoints, which can be extended to work with a react frontend

## Getting started:

```shell
poetry install
poetry shell
python -m uvicorn server.asgi:application --reload --reload-include "*.html"
```

```bash
$ poetry shell
$ python -m pytest
```

If you want pytest to fall into an ipython debugger shell on first failure

```bash
$ python -m pytest --pdbcls=IPython.core.debugger:Pdb -s
```

Auto Lint using https://github.com/psf/black, isort and flake8
```bash
$ black src
$ isort src --filter-files --profile black
$ flake8 --ignore=E501, W503, E722 --max-line-length=100 --max-complexity=10 src/
```

## Testing gitlab pipeline on localmachine

It's possible to install gitlab runner on your local machine and test the .gitlab-ci.yaml

```bash
$ gitlab-runner exec docker test\ python
```

## Deployment

For running in production

```shell
python -m gunicorn server.asgi:application -k uvicorn.workers.UvicornWorker
```

