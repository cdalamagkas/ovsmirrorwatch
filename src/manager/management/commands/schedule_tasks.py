from celery import shared_task
from celery.utils.log import get_task_logger
from api_ovs.OvsApi import OVSAPI
from manager.models import OVSManager
from django_celery_beat.models import PeriodicTask, PeriodicTasks, IntervalSchedule
from constance import config
from django.core.management.base import BaseCommand
import logging
import json
import manager.tasks


logger = get_task_logger(__name__)


class Command(BaseCommand):
    help = "This command schedules tasks for monitoring the OVSDB Managers."

    def handle(self, *args, **kwargs):
        self.stdout.write("Activated schedule_tasks", ending="")
        INTERVAL = config.REFRESH_INTERVAL_SECONDS
        managers = OVSManager.objects.all()
        schedule, _ = IntervalSchedule.objects.get_or_create(every=INTERVAL, period=IntervalSchedule.SECONDS)
        for manager in managers:
            logging.warning("Manager " + manager.name + " is enabled: " + str(manager.monitor))
            if PeriodicTask.objects.filter(name=manager.name).exists():
                manager_task = PeriodicTask.objects.get(name=manager.name)
                manager_task.enabled = manager.monitor
                manager_task.interval = schedule
                manager_task.save()
            else:
                PeriodicTask.objects.create(name=manager.name,
                                            task='manager.tasks.check_ovsdb_manager',
                                            interval=schedule,
                                            enabled=False,
                                            args=json.dumps([manager.name]))
