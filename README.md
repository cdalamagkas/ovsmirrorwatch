# OVSMirrorWatch :eyes: - An Open vSwitch Mirror Monitor tool

This is a Django-based web application that monitors OVSDB managers and restores their port mirroring configurations.

In Open vSwitch (OVS), port mirroring configurations are lost when the system reboots, and permanently breaks when a participating interface is removed. So, each time a port mirroring breaks or deleted, the system administrator should re-create again the port mirroring configurations. The same problem appears in cloud environments, e.g. in Proxmox VE.

To address this issue, OVSMirrorWatch allows the administrator to define port mirroring sessions, and then it queries periodically the OVSDB managers to ensure that the port mirroring sessions are present. If a port mirroring session breaks (due to a hard reboot of a VM or a downtime of some VMs), OVSMirrorWatch tries periodically to re-establish the port mirroring session. OVSMirrorWatch always ensures that the stateful mirroring configuration that the administrator defines in OVSMirrorWatch's DB, is reflected to the live and stateless enviroment of the OVSDB managers.

## Deployment from source code
If this is the first time running the project, you need to prepare the python environment and install the dependencies from `requirements.txt`. Also, make sure you are using Python 3.10.

If you do not have Python 3.10 in your system, issue the following commands on an Ubuntu machine:

```shell
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.10 python3.10-venv
```

Then, create a Python environment and activate it:

```shell
python3.10 -m venv venv
source ./venv/bin/activate
```

In your Python environment, install the dependencies in `requirements.txt` and (manually) the `python-ovs-vsctl` package:
```shell
pip install -r requirements.txt
pip install git+https://github.com/iwaseyusuke/python-ovs-vsctl.git
```

A `.env` file must be created (not included in git), which defines all the initial configurations that Django needs in order to start. The `.env` must have the following content:

```env
DJANGO_SECRET_KEY=<Django secret>
DJANGO_DEBUG=<0 or 1>
OVSMW_DJANGO_STATIC_FILES_PROXIED=1
OVSMW_REDIS_BROKER_HOST=<Use your own Redis server or uncomment the lines in docker-compose.yml to deploy one>
OVSMW_REDIS_BROKER_PORT=6379
DJANGO_INITIALIZE_SUPERUSER=1
DJANGO_SUPERUSER_USERNAME=<Provide a username for the built-in superuser>
DJANGO_SUPERUSER_PASSWORD=<Provide the password of the built-in superuser>
DJANGO_SUPERUSER_EMAIL=<Provide the email of the built-in superuser>
DJANGO_ALLOWED_HOSTS=*
```

Activate the virtual enviroment:
```shell
source ./venv/bin/activate
```

Load the environment variables
```shell
export $(cat .env | xargs)
```

If this is the first time starting the project, apply the migrations (also apply them every time the migrations are updated):
```shell
python manage.py migrate
```

If this is the first time starting the project, create a superuser:
```shell
python manage.py createsuperuser --noinput
```

Start the Celery worker in one window
```shell
celery -A ovsmirrorwatch worker -l info
```

In another window or terminal tab, **load again the environment variables**, and start the Celery Beat
```shell
celery -A ovsmirrorwatch beat -l info --scheduler django
```

Only for development purposes only, you can run the worker and beat with a single command:
```shell
celery -A ovsmirrorwatch worker --beat --scheduler django --loglevel=info
```

Finally, in another terminal window/tab, **load again the environment variables** and start the Django development server
```shell
python manage.py runserver 0.0.0.0:8000
```
