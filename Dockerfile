# pull official base image
FROM python:3.10-slim

# set work directory
WORKDIR /code

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install dependencies
COPY ./requirements.txt .

RUN apt update \
    && pip install -r requirements.txt \
    && pip install git+https://github.com/iwaseyusuke/python-ovs-vsctl.git

# Copy source code to /code/
COPY src .

EXPOSE 8000

RUN chmod +x entrypoint.sh

# run entrypoint.prod.sh
CMD ["/code/entrypoint.sh"]
