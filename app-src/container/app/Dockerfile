FROM cool-app-base:latest
MAINTAINER Nico Coetzee <nicc777@gmail.com>

LABEL Description="A container for the production hosting of a flask application" Vendor="none" Version="0.1"

# Install the app
WORKDIR /usr/src/app
RUN mkdir dist
COPY dist/*.tar.gz ./dist/
RUN pip3 install dist/*.tar.gz

COPY dist/*.y* /opt/

ENV SWAGGER_UI 0
ENV SPECIFICATION_DIR /opt
ENV DB_HOST coolapp-db
ENV DB_PORT 5432
ENV DB_USER postgres
ENV DB_PASS mysecretpassword
ENV DB_NAME coolapp
ENV LOG_LEVEL INFO

# Operational Configuration
EXPOSE 8080
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "--access-logfile", "-", "cool_app.service_app:app"]
