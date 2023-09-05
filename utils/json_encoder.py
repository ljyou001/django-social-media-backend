from django.core.serializers.json import DjangoJSONEncoder
from django.utils.duration import duration_iso_string
from django.utils.functional import Promise
from django.utils.timezone import is_aware

import datetime
import decimal
import uuid

class JSONEncoder(DjangoJSONEncoder):
    """
    This JSON encoder originally from DjangoJSONEncoder
    We need to re-write the default method to support a more precise datetime

    Why?
    Because we used created time to order the tweets, in case of ordering problems,
    we need to use the time as precise as possible.
    In Django, it will only provide microsecond precision by default to support ECMA-
    262 specification. This function is to eliminate it and provide the millisecond 
    precision.
    """

    def default(self, o):
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            # if o.microsecond:
            #     r = r[:23] + r[26:]
            # Commented this part, we don't use ECMA-262 specification.
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, datetime.timedelta):
            return duration_iso_string(o)
        elif isinstance(o, (decimal.Decimal, uuid.UUID, Promise)):
            return str(o)
        else:
            return super().default(o)