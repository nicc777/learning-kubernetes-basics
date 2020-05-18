FROM locustio/locust
USER root
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip3 install sqlalchemy psycopg2-binary
USER locust
ENV DB_HOST coolapp-db
ENV DB_PORT 5432
ENV DB_USER postgres
ENV DB_PASS mysecretpassword
ENV DB_NAME coolapp
ENV MAX_USERS 100