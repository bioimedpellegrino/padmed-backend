import datetime
from django.core.management.base import BaseCommand, CommandError
from auditlog.models import LogEntry
from custom_logger.models import Logger, WebRequest

class Command(BaseCommand):
    help = 'Deploy a specific entity by id'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=str,
            help='Days to delete',
        )


    def handle(self, *args, **options):
        if options['days']:
            dt = datetime.datetime.now() - datetime.timedelta(days=int(options['days']))
            entries = LogEntry.objects.filter(timestamp__lte=dt)
            print('deleting %s adudilog' % len(entries))
            entries.delete()

            entries = Logger.objects.filter(date__lte=dt)
            print('deleting %s logs' % len(entries))
            entries.delete()

            entries = WebRequest.objects.filter(time__lte=dt)
            print('deleting %s web requests' % len(entries))
            entries.delete()

            print('Done')