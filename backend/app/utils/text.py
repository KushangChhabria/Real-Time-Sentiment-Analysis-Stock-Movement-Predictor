import re

_clean_re = re.compile(r"\s+")


def clean_text(s: str) -> str:
    s = s.strip()
    s = _clean_re.sub(" ", s)
    return s
