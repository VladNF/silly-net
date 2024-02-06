FROM python:3.11.1
COPY ./vendor /vendor
RUN pip install -r /vendor/prod.txt

WORKDIR /snet
COPY ./app /snet/app
ENV PYTHONPATH=/snet
