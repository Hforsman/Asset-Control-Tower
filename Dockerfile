FROM python:3.8-buster

ENV MYSQL_HOST=rust_eze

COPY requirements.txt ./
COPY Makefile ./
RUN make venv

COPY constants.py ./
COPY database.py ./
COPY main.py ./
COPY utils.py ./

CMD ["venv/bin/python3"]