from triage.models import *


def init_triage():
    triage_codes = ['WHITE', 'GREEN','YELLOW']
    for triage_code in triage_codes:
        triage_code, _ = TriageCode.objects.get_or_create(code=triage_code)

def init_reasons(hospital):
    reasons = [
                ("VALUTAZIONE GENERALE", 1, "WHITE"),
                ("INFORTUNIO SUL LAVORO", 2, "YELLOW"),
                ("MALESSERE", 3, "GREEN"),
                ("CONTUSIONE",4, "YELLOW"),
                ("DIFFICOLTA' A RESPIRARE", 5, "YELLOW"),
                ("FERITA", 6, "YELLOW"),
                ("DOLORE ADDOMINALE", 7, "YELLOW"),
                ("ALTRO", 8, "WHITE")
            ]
    
    for reason_pack in reasons:
        r = TriageAccessReason()
        r.hospital = hospital
        r.reason = reason_pack[0]
        r.order = reason_pack[1]
        r.related_code = TriageCode.objects.get(code=reason_pack[2])
        r.save()
    
    



