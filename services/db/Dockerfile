FROM python:3.11-alpine3.19
RUN pip install psycopg2-binary yoyo-migrations==8.2.0
COPY ./migrations /yoyo/migrations
COPY ./yoyo.ini /yoyo
COPY ./migrate.sh /yoyo
WORKDIR /yoyo
