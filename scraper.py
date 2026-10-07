"""Coordinate fetching and extracting company website data."""

import requests

from app.extractor import CompanyData, extract_company_data
from app.validator import DEFAULT_TIMEOUT, check_url_reachable


def scrape_url(url: str, timeout: int = DEFAULT_TIMEOUT) -> CompanyData:
    """Scrape one company website, returning errors as structured data."""
    try:
        response = check_url_reachable(url, timeout=timeout)
    except (ValueError, requests.RequestException) as error:
        return CompanyData(website_url=url, error=str(error))

    return extract_company_data(response.text, url)