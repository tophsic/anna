FROM python:2

MAINTAINER Christophe Sicard <sicard.christophe+docker@gmail.com>

RUN pip install tox

COPY . /opt/anna
WORKDIR /opt/anna

RUN tox

EXPOSE 9000

CMD [ ".tox/py27/bin/python", "run_will.py" ]
