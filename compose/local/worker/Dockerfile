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
  && apk add gettext

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /app/requirements
RUN pip install -r /app/requirements/local.txt

# copy worker start file
COPY ./compose/local/worker/start_worker /start_worker
RUN sed -i 's/\r//' /start_worker
RUN chmod +x /start_worker

# copy beat start file
COPY ./compose/local/worker/start_beat /start_beat
RUN sed -i 's/\r//' /start_beat
RUN chmod +x /start_beat

EXPOSE 8100

# add the local files into the docker container
COPY ./dapp_store_backend /app/dapp_store_backend

WORKDIR /app
