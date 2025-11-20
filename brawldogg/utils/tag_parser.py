import re

TAG_REGEX = re.compile(r"^#?([A-Z0-9]{3,})$", re.IGNORECASE)


def normalize_tag(tag: str) -> str:
    """
    Validates a Brawl Stars tag (player or club) and returns it in
    URL-safe format (e.g., #ABC -> %23ABC).
    """
    if not (match := TAG_REGEX.match(tag.strip())):
        raise ValueError(f"Invalid player/club tag: {tag!r}")

    # The API requires '#' to be URL-encoded as %23
    return f"%23{match.group(1).upper()}"
