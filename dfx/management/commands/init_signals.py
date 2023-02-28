from django.core.management.base import BaseCommand, CommandError
from dfx.models import DeepAffexPoint
import pandas as pd
class Command(BaseCommand):
    help = 'Init the DeepAffex Points'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        
        signals = pd.read_excel("dfx/management/commands/deep_affex_signals.xls")
        for _index, signal in signals.iterrows():
            deep_affex_point, _c = DeepAffexPoint.objects.get_or_create(signal_key=signal['KEY'])
            deep_affex_point.signal_key = signal['KEY']
            deep_affex_point.signal_name = signal['NAME']
            deep_affex_point.signal_name_ita = signal['NAME_ITA']
            deep_affex_point.signal_description = signal['DESCR']
            deep_affex_point.signal_config = signal['CONFIG']
            deep_affex_point.signal_unit = "" if signal['UNIT'] == 'None' else signal['UNIT'] 
            deep_affex_point.multiplier = float(signal['MULTIPLIER'])
            deep_affex_point.limit_value = float(signal['LIMIT_VALUE'])
            deep_affex_point.is_measure = True if str(signal['IS_MEASURE']).strip() == 'True' else False
            deep_affex_point.save()