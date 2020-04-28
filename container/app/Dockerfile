FROM cool-app-base:latest
MAINTAINER Nico Coetzee <nicc777@gmail.com>

LABEL Description="A container for the production hosting of a flask application" Vendor="none" Version="0.1"

# Install the app
WORKDIR /usr/src/app
RUN mkdir dist
COPY dist/*.tar.gz ./dist/
RUN pip3 install dist/*.tar.gz

# Operational Configuration
EXPOSE 8080
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "--access-logfile", "-", "cool-app.app:app"]