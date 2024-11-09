# OVSMirrorWatch :eyes: - An Open vSwitch Mirror Monitor tool

This is a Django-based web application that monitors OVSDB managers and restores their port mirroring configurations.

> Explain Motivation

To address this issue, OVSMirrorWatch allows the administrator to define port mirroring sessions, and then it queries periodically the OVSDB managers to ensure that the port mirroring sessions are present. If a port mirroring session breaks (due to a hard reboot of a VM or a downtime of some VMs), OVSMirrorWatch tries periodically to re-establish the port mirroring session. OVSMirrorWatch always ensures that the stateful mirroring configuration that the administrator defines in OVSMirrorWatch's DB, is reflected to the live and stateless enviroment of the OVSDB managers.

## Deployment from source code
If this is the first time running the project, you need to prepare the python environment and install the dependencies from `requirements.txt`. Also, make sure you are using Python 3.10.

In your Python environment, install `python-ovs-vsctl`:
```shell
pip install git+https://github.com/iwaseyusuke/python-ovs-vsctl.git
```

A `.env` file must be created (not included in git), which defines all the initial configurations that Django needs in order to start. The `.env` must have the following content:

```env
OVSMW_SECRET_KEY=<Django secret>
OVSMW_DEBUG=<0 or 1>
OVSMW_DJANGO_STATIC_FILES_PROXIED=<0 or 1>
OVSMW_REDIS_BROKER_HOST=<You can use docker-lab.trsc.net or your own Redis server>
OVSMW_REDIS_BROKER_PORT=<Usually 6379>
```

> Redis is an essential component, it is required by Django Celery, Celery Beat and Django Channels!

Activate the virtual enviroment:
```shell
source ./venv/bin/activate
```

Load the environment variables
```shell
export $(cat .env | xargs)
```

Start the Celery worker in one window
```shell
celery -A ovsmirrorwatch worker -l info
```

In another window or terminal tab, **load again the environment variables**, and start the Celery Beat
```shell
celery -A ovsmirrorwatch beat -l info
```

Finally, in another terminal window/tab, **load again the environment variables** and start the Django development server
```shell
python manage.py runserver 0.0.0.0:8000
```

## ovs_mirror_monitor and OVSAPI

The script monitors the state of the mirrors currently configured. It uses the ovs-vsctl cmd tool wrapped as a python script to interact with the ovs-db in the machine running the mirrors. Every 5 seconds the script fetches the current port mirrorings and keeps an internal state of said port mirrors. If in the next poll the states have changed the script attempts to re-establish the failed port mirrors based on the stored mirror state form the previous 5 seconds.

### To build the image run:
```docker build -t mirror_monitor .```

### To run the image:
``` docker run -it --net=host  mirror_monitor ```
