FROM cool-app-base:latest
MAINTAINER Nico Coetzee <nicc777@gmail.com>

LABEL Description="A container for the production hosting of a flask application" Vendor="none" Version="0.1"

# Install the app
WORKDIR /usr/src/app
RUN mkdir dist
COPY dist/*.tar.gz ./dist/
RUN pip3 install dist/*.tar.gz

COPY dist/*.y* /opt/

ENV SWAGGER_UI 1
ENV SPECIFICATION_DIR /opt

# Operational Configuration
EXPOSE 8080
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "--access-logfile", "-", "cool_app.service_app:app"]
