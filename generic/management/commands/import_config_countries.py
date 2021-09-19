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
    help = 'Import ConfigurationCountry'

    def add_arguments(self, parser):
        parser.add_argument('preview', type=str)
        parser.add_argument('debug', type=str)
        parser.add_argument('local_file_name_with_ext', type=str)
        parser.add_argument('language_code', type=str)

    def handle(self, *args, **options):
        is_preview = True if options['preview'] and options['preview'].lower() == 'true' else False
        is_debug = True if options['debug'] and options['debug'].lower() == 'true' else False
        local_file_name_with_ext = options['local_file_name_with_ext'] if options['local_file_name_with_ext'] else None
        language_code = options['language_code'].lower()
        
        count_rows_with_data = 0

        if local_file_name_with_ext:

            import_date = datetime.datetime.now()

            print('----------------')
            print('preview: %s' % is_preview)
            print('debug: %s' % is_debug)
            print('local_file_name_with_ext: %s' % local_file_name_with_ext)
            print('import_date: %s' % datetime.datetime.strftime(import_date, '%d/%m/%Y'))
            print('-----------------------------------')

            add_log(level=2, message=5, custom_message='import_config_countries - IN - import_date %s - is_preview %s - local_file_name_with_ext %s' % (datetime.datetime.strftime(import_date, '%d/%m/%Y'), is_preview, local_file_name_with_ext))

            source_file_path = 'core/management/commands/%s' % local_file_name_with_ext

            data_factory = pd.read_csv(source_file_path, encoding='latin1', sep=';')

            add_log(level=2, message=5, custom_message='import_config_countries - Count rows from input file: %s' % len(data_factory))
            print('Count rows from input file: %s' % len(data_factory))
            print('------------------------------------------------------------------------------------------')

            for _index, item in data_factory.iterrows():
                if item["Denominazione IT"] and str(item["Denominazione IT"]).lower() != 'nan':
                    count_rows_with_data = count_rows_with_data + 1

            add_log(level=2, message=5, custom_message='import_config_countries - Count rows with data from input file: %s' % count_rows_with_data)
            print('Count rows with data from input file: %s' % count_rows_with_data)
            print('------------------------------------------------------------------------------------------')

            check_import = self.__import_countries(data_factory, import_date, count_rows_with_data, is_preview=is_preview, is_debug=is_debug, language_code=language_code)

            # if check_import:
            #     self.__delete_previous_countries(import_date, is_preview=is_preview)
            # else:
            #     self.__rollback_imported_countries(import_date, is_preview=is_preview)

            add_log(level=2, message=5, custom_message='import_config_countries - OUT - import_date %s - is_preview %s - local_file_name_with_ext %s' % (datetime.datetime.strftime(import_date, '%d/%m/%Y'), is_preview, local_file_name_with_ext))


    def __import_countries(self, data_factory, import_date, count_rows_with_data, is_preview=False, is_debug=False, language_code="it"):
        check_import = True
        countries_preview = []
        country_title = ''

        add_log(level=2, message=5, custom_message='import_config_countries - Import countries - IN')
        print('Import countries - IN')

        try:
            for _index, item in data_factory.iterrows():
                if language_code == 'it':
                    column_title = "Denominazione IT"
                elif language_code == 'en':
                    column_title = "Denominazione EN"
                else:
                    column_title = "Denominazione IT"
                    
                try:
                    if item[column_title] and str(item[column_title]).lower() != 'nan':
                        country_title = item[column_title]

                        c_item = ConfigurationCountry()
                        c_item.title = country_title
                        c_item.import_date = import_date
                        c_item.language_code = language_code
                        
                        if not is_preview:
                            if is_debug:
                                print('IMPORT COUNTRY - %s' % (c_item.title))
                            c_item.save()
                        else:
                            if is_debug:
                                print('PREVIEW MODE: IMPORT COUNTRY - %s' % (c_item.title))
                            countries_preview.append(c_item.title)

                except Exception as ex:
                    add_log(level=5, message=5, custom_message='import_config_countries - INNER EXCEPTION: %s' % ex)
                    print('INNER EXCEPTION: %s' % ex)
                    check_import = False

        except Exception as ex:
            add_log(level=5, message=5, custom_message='import_config_countries - EXCEPTION: %s' % ex)
            print('EXCEPTION: %s' % ex)
            check_import = False

        try:
            print('------------------------------------------------------------------------------------------')
            print('CHECK IMPORT RESULT')
            print('----------------------------------------')

            # check imported data
            print('data factory rows with data from input file: %s' % count_rows_with_data)

            if not is_preview:
                imported_countries = ConfigurationCountry.objects.filter(import_date=import_date)

                add_log(level=2, message=5, custom_message='import_config_countries - imported countries: %s' % imported_countries.count())
                print('imported countries: %s' % imported_countries.count())

                if check_import:
                    check_import = imported_countries.count() == count_rows_with_data
            else:
                print('PREVIEW MODE - imported countries: %s' % len(countries_preview))

                if check_import:
                    check_import = len(countries_preview) == count_rows_with_data

            print('----------------------------------------')
            add_log(level=2, message=5, custom_message='import_config_countries - CHECK IMPORTED COUNTRY RESULT: %s' % ('OK' if check_import else 'KO'))
            print('CHECK IMPORTED COUNTRY RESULT: %s' % ('OK' if check_import else 'KO'))
            print('------------------------------------------------------------------------------------------')

        except Exception as ex:
            add_log(level=5, message=5, custom_message='import_config_countries - CHECK RESULT EXCEPTION: %s' % ex)
            print('CHECK RESULT EXCEPTION: %s' % ex)
            check_import = False

        add_log(level=2, message=5, custom_message='import_config_countries - Import countries - OUT')
        print('Import countries - OUT')
        print('------------------------------------------------------------------------------------------')

        return check_import
    
    def __delete_previous_countries(self, import_date, is_preview=False):
        if not is_preview:
            add_log(level=2, message=5, custom_message='import_config_countries - DELETE ALL COUNTRIES with import_date < %s' % datetime.datetime.strftime(import_date, '%d/%m/%Y'))
            print('DELETE ALL COUNTRIES with import_date < %s' % datetime.datetime.strftime(import_date, '%d/%m/%Y'))

            items_to_delete = ConfigurationCountry.objects.filter(import_date__lt=import_date)

            add_log(level=2, message=5, custom_message='import_config_countries - DELETE %s countries' % items_to_delete.count())
            print('DELETE %s countries' % items_to_delete.count())

            items_to_delete.delete()
        else:
            print('PREVIEW MODE: DELETE ALL COUNTRIES with import_date < %s' % datetime.datetime.strftime(import_date, '%d/%m/%Y'))

        print('------------------------------------------------------------------------------------------')


    def __rollback_imported_countries(self, import_date, is_preview=False):
        if not is_preview:
            add_log(level=2, message=5, custom_message='import_config_countries - ROLLBACK ALL COUNTRIES with import_date = %s' % datetime.datetime.strftime(import_date, '%d/%m/%Y'))
            print('ROLLBACK ALL COUNTRIES with import_date = %s' % datetime.datetime.strftime(import_date, '%d/%m/%Y'))

            items_to_delete = ConfigurationCountry.objects.filter(import_date=import_date)

            add_log(level=2, message=5, custom_message='import_config_countries - DELETE %s countries' % items_to_delete.count())
            print('DELETE %s countries' % items_to_delete.count())

            items_to_delete.delete()
        else:
            print('PREVIEW MODE: ROLLBACK ALL COUNTRIES with import_date = %s' % datetime.datetime.strftime(import_date, '%d/%m/%Y'))

        print('------------------------------------------------------------------------------------------')
