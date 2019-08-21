FROM python:3.6-alpine

ENV PYTHONUNBUFFERED 1

RUN apk update \
  # psycopg2 dependencies
  && apk add --virtual build-deps gcc python3-dev musl-dev \
  && apk add postgresql-dev \
  # Pillow dependencies
  && apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
  # CFFI dependencies
  && apk add libffi-dev py-cffi

RUN addgroup -S flask \
    && adduser -S -G flask flask

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/production.txt \
    && rm -rf /requirements

COPY ./compose/production/flask/entrypoint /entrypoint
RUN sed -i 's/\r//' /entrypoint
RUN chmod +x /entrypoint
RUN chown flask /entrypoint

COPY ./compose/production/flask/start /start
RUN sed -i 's/\r//' /start
RUN chmod +x /start
RUN chown flask /start

# add the local files into the docker container
COPY ./dapp_store_backend /app/dapp_store_backend
COPY ./migrations /app/migrations
COPY ./wsgi.py /app

RUN chown -R flask /app

USER flask

WORKDIR /app

ENTRYPOINT ["/entrypoint"]

CMD ["/start"]