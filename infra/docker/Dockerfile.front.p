FROM python:3.11.8-alpine3.19
COPY ./services/python/front/vendor /vendor
RUN pip install -r /vendor/prod.txt

WORKDIR /snet
COPY ./services/python/front/app /snet/app
ENV PYTHONPATH=/snet
