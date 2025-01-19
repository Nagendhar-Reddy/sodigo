import hashlib
import re
from datetime import datetime, timedelta

BASE_URL = "https://short.ly/"

def generate_short_url(long_url):
    hash_object = hashlib.sha256(long_url.encode())
    return BASE_URL + hash_object.hexdigest()[:6]

def validate_url(url):
    regex = re.compile(
        r'^(https?://)?'  # http:// or https://
        r'([a-z0-9.-]+)\.'  # domain
        r'[a-z]{2,6}'  # TLD
        r'(/.*)?$'  # Path
    )
    return re.match(regex, url)

def get_expiry_time(hours=None):
    return datetime.now() + timedelta(hours=hours or 24)
