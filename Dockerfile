FROM python:3.8-alpine AS geeksbot

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 1

RUN adduser --disabled-password --home=/home/geeksbot --gecos "" geeksbot
RUN echo "geeksbot ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN echo "geeksbot:docker" | chpasswd

RUN apk update && \
        apk add --virtual build-deps gcc python3-dev musl-dev postgresql-dev \
        # Pillow dependencies
        && apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
        # CFFI dependencies
        && apk add libffi-dev py-cffi \
        # Translations dependencies
        && apk add gettext \
        # https://docs.djangoproject.com/en/dev/ref/django-admin/#dbshell
        && apk add postgresql-client

RUN mkdir /code
WORKDIR /code

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN pip install --upgrade pip
RUN pip install virtualenv

WORKDIR /code

COPY /code/geeksbot_v2/requirements/base.txt .
COPY /code/geeksbot_v2/requirements/production.txt .
COPY /code/geeksbot_v2/requirements/geeksbot.txt .
COPY /code/geeksbot_v2/.env .
COPY /code/geeksbot_v2/entrypoint .

RUN pip install -r production.txt
RUN pip install -r geeksbot.txt

CMD ["./entrypoint"]
