from django.dispatch import Signal
from django.dispatch import receiver
from django.core.management import call_command

# Define a custom signal
schedule_managers = Signal()


@receiver(schedule_managers)
def run_management_command(sender, **kwargs):
    # Run the management command
    call_command('schedule_tasks')
