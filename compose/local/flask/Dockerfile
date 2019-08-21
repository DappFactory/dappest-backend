FROM python:3.6-alpine

ENV PYTHONUNBUFFERED 1

RUN apk update \
  # psycopg2 dependencies
  && apk add --virtual build-deps gcc python3-dev musl-dev \
  && apk add postgresql-dev \
  # Pillow dependencies
  && apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
  # CFFI dependencies
  && apk add libffi-dev py-cffi \
  # Translations dependencies
  && apk add gettext \
  # https://docs.flaskproject.com/en/dev/ref/flask-admin/#dbshell
  && apk add postgresql-client

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install -r /requirements/local.txt

# copy entrypoint file
COPY ./compose/production/flask/entrypoint /entrypoint
RUN sed -i 's/\r//' /entrypoint
RUN chmod +x /entrypoint

# copy start file
COPY ./compose/local/flask/start /start
RUN sed -i 's/\r//' /start
RUN chmod +x /start

# copy test file
COPY ./compose/local/flask/test /test
RUN sed -i 's/\r//' /test
RUN chmod +x /test

EXPOSE 8000

# add the local files into the docker container
COPY ./dapp_store_backend /app/dapp_store_backend
COPY ./manage.py /app

WORKDIR /app

ENTRYPOINT ["/entrypoint"]
