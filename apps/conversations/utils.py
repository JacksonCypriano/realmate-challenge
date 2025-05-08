from dateutil.parser import parse as parse_datetime
from django.utils.timezone import make_aware, is_naive

def parse_webhook_timestamp(timestamp_str):
    dt = parse_datetime(timestamp_str)
    if is_naive(dt):
        dt = make_aware(dt)
    return dt
