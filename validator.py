"""URL validation and page reachability checks."""

from urllib.parse import urlparse

import requests


DEFAULT_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 (compatible; CompanyDataScraper/1.0)"


def validate_url(url: str) -> bool:
    """Return whether the value is an absolute HTTP(S) URL."""
    if not isinstance(url, str):
        return False

    try:
        parsed = urlparse(url.strip())
        return (
            parsed.scheme.lower() in {"http", "https"}
            and bool(parsed.netloc)
            and bool(parsed.hostname)
        )
    except (ValueError, TypeError):
        return False


def check_url_reachable(url: str, timeout: int = DEFAULT_TIMEOUT) -> requests.Response:
    """Fetch a URL once and raise for network or HTTP status errors."""
    if not validate_url(url):
        raise ValueError("Invalid URL format")

    response = requests.get(
        url.strip(),
        timeout=timeout,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    return response