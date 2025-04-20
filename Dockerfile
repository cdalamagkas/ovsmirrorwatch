FROM python:3.10-slim-bullseye

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
COPY entrypoint.sh .

RUN apt update \
    && apt install -y git wget \
    && pip install -r requirements.txt \
    && pip install git+https://github.com/iwaseyusuke/python-ovs-vsctl.git \
    && wget http://snapshot.debian.org/archive/debian/20190501T215844Z/pool/main/g/glibc/multiarch-support_2.28-10_amd64.deb \ 
    && dpkg -i multiarch-support*.deb \
    && wget http://snapshot.debian.org/archive/debian/20170705T160707Z/pool/main/o/openssl/libssl1.0.0_1.0.2l-1%7Ebpo8%2B1_amd64.deb \
    && dpkg -i libssl1.0.0*.deb 

COPY src .

EXPOSE 8000

RUN chmod +x entrypoint.sh

CMD ["/code/entrypoint.sh"]
