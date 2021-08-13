FROM python:3.7-slim-stretch AS base
RUN pip install virtualenv
RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y make gcc wget
RUN pip install uwsgi
RUN groupadd -g 999 appuser && \
    useradd -m -r -u 999 -g appuser appuser

FROM base as release
EXPOSE 8000
RUN rm -fr /sources/media/*
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz
USER appuser
COPY --chown=appuser:appuser requirements.txt Makefile /sources/
RUN mkdir -p /sources/collected_static && chown -R appuser:appuser /sources/collected_static
WORKDIR /sources
RUN make init 
COPY --chown=appuser:appuser . /sources
ENTRYPOINT ["/sources/docker-entrypoint.sh"]
CMD  dockerize -wait tcp://db:5432 -timeout 10s uwsgi --ini uwsgi.ini

FROM base as test
COPY --from=release --chown=appuser:appuser /sources /sources
COPY --from=release --chown=appuser:appuser /home/appuser/.cache  /home/appuser/.cache
USER appuser
RUN mkdir -p /sources/collected_static && chown -R appuser:appuser /sources/collected_static
WORKDIR /sources
ENTRYPOINT ["/sources/docker-entrypoint.sh"]
CMD make test 

