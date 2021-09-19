import datetime
import os
import uuid
import pandas as pd
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import ConfigurationCountry
from custom_logger.utils import add_log

class Command(BaseCommand):
    help = 'Import Dialog Codes'

    def add_arguments(self, parser):
        parser.add_argument('preview', type=str)
        parser.add_argument('local_file_name_with_ext', type=str)
        parser.add_argument('language_code', type=str)

    def handle(self, *args, **options):
        is_preview = True if options['preview'] and options['preview'].lower() == 'true' else False
        local_file_name_with_ext = options['local_file_name_with_ext'] if options['local_file_name_with_ext'] else None
        language_code = options['language_code'].lower()
        
        count_rows_with_data = 0

        if local_file_name_with_ext:

            import_date = datetime.datetime.now()

            print('----------------')
            print('preview: %s' % is_preview)
            print('local_file_name_with_ext: %s' % local_file_name_with_ext)
            print('language_code: %s' % language_code)
            print('import_date: %s' % datetime.datetime.strftime(import_date, '%d/%m/%Y'))
            print('-----------------------------------')

            add_log(level=2, message=5, custom_message='import_config_countries - IN - import_date %s - is_preview %s - local_file_name_with_ext %s' % (datetime.datetime.strftime(import_date, '%d/%m/%Y'), is_preview, local_file_name_with_ext))

            source_file_path = 'core/management/commands/%s' % local_file_name_with_ext

            data_factory = pd.read_excel(source_file_path)
            print('Count rows from input file: %s' % len(data_factory))
            print('------------------------------------------------------------------------------------------')
            i = 0
            for _index, item in data_factory.iterrows():
                country_name = item['Country ']
                cfc = ConfigurationCountry.objects.filter(title=country_name.strip(), language_code='en').first()
                if cfc:
                    cfc.dialog_code = "(%s)" %item['International dialing']
                    if not is_preview:
                        cfc.save()

            add_log(level=2, message=5, custom_message='import_config_countries - OUT - import_date %s - is_preview %s - local_file_name_with_ext %s' % (datetime.datetime.strftime(import_date, '%d/%m/%Y'), is_preview, local_file_name_with_ext))
