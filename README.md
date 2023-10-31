# django-llama2-reactjs-chat-pdf

A python LLM chat app using Django Async, ReactJS and LLAMA2, that allows you to chat with multiple pdf documents
Components are chose so everything can be self-hosted.


Project using LLAMA2 hosted via replicate - however, you can self-host your own LLAMA2 instance.

This project is hosted on [GitHub](https://github.com/pgryko/django-llama2-reactjs-chat-pdf) and [GitLab](https://gitlab.com/pgryko/django-llama2-reactjs-chat-pdf)


![Project Demo](./demo-15fps.gif)

## Getting started:

Django Server instructions exist [Here](server/README.md)

If there is time a client folder will be created, running a reactjs client

## Gitlab runner

If you've configured a gitlab runner locally, you can test the gitlab ci via

```shell
gitlab-runner exec docker test\ python
```


## License
MIT
