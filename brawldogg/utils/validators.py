from datetime import datetime
from pydantic import field_validator


def parse_time(value: str) -> datetime:
    """Parses '20251118T183123.000Z' into a datetime object."""
    return datetime.strptime(value, "%Y%m%dT%H%M%S.%fZ")


time_validator = field_validator(
    "battle_time", "start_time", "end_time", mode="before", check_fields=False
)(parse_time)
