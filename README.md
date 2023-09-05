# django-llama2-reactjs-chat-pdf

A python LLM chat app using Django Async, ReactJS and LLAMA2, that allows you to chat with multiple pdf documents.
Components are chose so everything can be self-hosted.


Project using LLAMA2 hosted via replicate - however, you can self-host your own LLAMA2 instance.

This project is hosted on [GitHub](https://github.com/pgryko/django-llama2-reactjs-chat-pdf) and [GitLab]
(https://gitlab.com/pgryko/django-llama2-reactjs-chat-pdf), but maintained on [GitLab](https://gitlab.
com/pgryko/django-llama2-reactjs-chat-pdf).

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



## License
MIT
