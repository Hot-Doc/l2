from typing import List

from astm import codec
from collections import defaultdict
from django.utils import timezone
import directions.models as directions
import directory.models as directory
import api.models as api


def get_astm_header() -> list:
    return ['H', [[None], [None, '&']], None, None, ['1', '2.00'], None, None, None, None, None, None, 'P', '1.00', timezone.now().strftime("%Y%m%d%H%M%S")]


def get_leave() -> list:
    return ['L', 1, 'N']


def get_patient() -> list:
    return ['P', 1, None, None, ['', '', '', '']]


def get_iss_direction(direction: directions.Napravleniya, analyzer: api.Analyzer, full=False) -> list:
    r = []
    n = 0
    iss_list = directions.Issledovaniya.objects.filter(napravleniye=direction)
    if not full:
        iss_list = iss_list.filter(doc_confirmation__isnull=True)
    for i in iss_list:
        researches = defaultdict(list)
        for fraction in directory.Fractions.objects.filter(research=i.research, relationfractionastm__analyzer=analyzer, hide=False):
            rel = api.RelationFractionASTM.objects.filter(fraction=fraction, analyzer=analyzer)
            if not rel.exists():
                continue
            rel = rel[0]
            tube = directions.TubesRegistration.objects.filter(type__fractions=fraction)
            if not tube.exists():
                continue
            tube = tube[0]
            researches[tube.pk].append(rel.astm_field)
        for tpk in researches:
            n += 1
            r.append(['O', n, tpk, None, [[None, x, None, None] for x in researches[tpk]]])
    return r


def encode(m) -> list:
    return codec.encode(m)


def get_astm(directions_list: List[directions.Napravleniya], analyzer: api.Analyzer, full=False) -> list:
    return encode([get_astm_header(), get_patient()] + [get_iss_direction(x, analyzer, full) for x in directions_list] + [get_leave()])
