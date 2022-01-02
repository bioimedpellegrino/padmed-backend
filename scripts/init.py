from triage.models import *


def init_triage():
    triage_codes = ['WHITE', 'GREEN','YELLOW']
    for triage_code in triage_codes:
        triage_code, _ = TriageCode.objects.get_or_create(code=triage_code)

def init_reasons(hospital):
    reasons = ['INCIDENTE','MALESSERE','ALTRO','CONTUSIONE','FERITA','DOLORE ADDOMINALE','DOLORE GENERALE','INFORTUNIO SUL LAVORO']
    for reason in reasons:
        r = TriageAccessReason()
        r.hospital = hospital
        r.reason = reason
        r.save()
    