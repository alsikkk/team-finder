import re

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

PHONE_PATTERN = re.compile(r"^(8\d{10}|\+7\d{10})$")
GITHUB_HOST = "github.com"


def normalize_phone(phone):
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) == 11 and digits.startswith("8"):
        return f"+7{digits[1:]}"
    if len(digits) == 11 and digits.startswith("7"):
        return f"+7{digits[1:]}"
    return phone


def validate_phone_format(phone):
    normalized = normalize_phone(phone)
    if not PHONE_PATTERN.match(normalized):
        raise ValidationError("Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX.")
    return normalized


def validate_github_url(url):
    if not url:
        return url
    validator = URLValidator()
    validator(url)
    if GITHUB_HOST not in url.lower():
        raise ValidationError("Ссылка должна вести на GitHub.")
    return url
