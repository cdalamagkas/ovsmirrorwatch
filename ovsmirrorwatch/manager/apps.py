from django.apps import AppConfig
from django.core.cache import cache  # Optional: use to ensure one-time execution
from django.core.management import call_command
import logging
from django.db.models.signals import post_migrate
from .signals import schedule_managers


class ManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'manager'

    def ready(self):
        # Connect to Django's `post_migrate` signal to ensure migrations are complete
        post_migrate.connect(self.run_command_after_all_apps_loaded)

    def run_command_after_all_apps_loaded(self, **kwargs):
        # Emit the custom signal
        schedule_managers.send(sender=self.__class__)

        # Optionally, you can directly call a management command here
        # call_command('your_command_name')

