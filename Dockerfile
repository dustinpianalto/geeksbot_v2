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

COPY requirements/base.txt .
COPY requirements/production.txt .
COPY requirements/geeksbot.txt .

RUN pip install -r production.txt
RUN pip install -r geeksbot.txt

ENV REDIS_DB 0
ENV REDIS_HOST ip-10-0-0-4.ec2.internal
ENV REDIS_PORT 6379
ENV REDIS_PASSWORD EUZ9QWkaFhMM
ENV USE_DOCKER yes
ENV DISCORD_DEFAULT_PREFIX g$
ENV PYTHONPATH /code

COPY entrypoint .

CMD ["./entrypoint"]
