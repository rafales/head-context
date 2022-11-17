from html import escape

from typing_extensions import Protocol


class SafeHTML(Protocol):
    def __html__(self) -> str:
        pass


def clean_key(key):
    key = key.rstrip("_")
    if key.startswith("data_") or key.startswith("aria_"):
        key = key.replace("_", "-")
    return key


def html_params(**kwargs):
    """
    Return a string of HTML attributes from the given keyword arguments.
    """
    params = []
    for k, v in sorted(kwargs.items()):
        k = clean_key(k)
        if v is True:
            params.append(k)
        elif v is False or v is None:
            pass
        else:
            params.append(f'{str(k)}="{escape(v)}"')
    return " ".join(params)
