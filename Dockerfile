FROM python:3.10-slim-bullseye

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
COPY entrypoint.sh .

RUN apt update \
    && apt install -y git \
    && pip install -r requirements.txt \
    && pip install git+https://github.com/iwaseyusuke/python-ovs-vsctl.git

COPY src .

EXPOSE 8000

RUN chmod +x entrypoint.sh

CMD ["/code/entrypoint.sh"]
