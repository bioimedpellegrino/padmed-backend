from django.core.management.base import BaseCommand, CommandError
from mail.utils import send_msgs


class Command(BaseCommand):
    help = 'Send all mail messages with errors'

    def handle(self, *args, **options):

        send_msgs()
