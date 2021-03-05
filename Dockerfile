FROM python:3.8-buster

ENV MYSQL_HOST=rust_eze
ENV PYTHONUNBUFFERED=yes

COPY . .
RUN make venv

CMD ["venv/bin/pytest", "test_all.py"]