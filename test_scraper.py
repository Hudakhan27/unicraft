from unittest.mock import Mock

import requests
import pytest

from app.extractor import extract_company_data
from app.scraper import scrape_url
from app.validator import check_url_reachable, validate_url


def test_validate_url_accepts_http_and_https():
    assert validate_url("https://example.com/path")
    assert validate_url("http://example.com")


def test_validate_url_rejects_invalid_values():
    assert not validate_url("example.com")
    assert not validate_url("ftp://example.com")
    assert not validate_url("https:///missing-host")


def test_check_url_reachable_raises_http_status_errors(monkeypatch):
    response = Mock()
    response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
    get = Mock(return_value=response)
    monkeypatch.setattr("app.validator.requests.get", get)

    with pytest.raises(requests.HTTPError, match="404 Not Found"):
        check_url_reachable("https://example.com", timeout=3)

    get.assert_called_once()
    assert get.call_args.kwargs["timeout"] == 3


def test_extract_company_data_from_html():
    html = """
    <html><head><title>Example Company</title>
    <script src="/assets/react-dom.js"></script></head>
    <body><p>Contact hello@example.com or +1 (555) 123-4567</p></body></html>
    """

    result = extract_company_data(html, "https://example.com")

    assert result.company_name == "Example Company"
    assert result.emails == ["hello@example.com"]
    assert result.phones == ["+1 (555) 123-4567"]
    assert "React" in result.tech_stack


def test_scrape_url_returns_extracted_data(monkeypatch):
    response = Mock(text="<title>Example</title><p>info@example.com</p>")
    monkeypatch.setattr("app.scraper.check_url_reachable", lambda *args, **kwargs: response)

    result = scrape_url("https://example.com")

    assert result.company_name == "Example"
    assert result.emails == ["info@example.com"]


def test_scrape_url_returns_network_errors_as_data(monkeypatch):
    def fail_fetch(*args, **kwargs):
        raise requests.Timeout("request timed out")

    monkeypatch.setattr("app.scraper.check_url_reachable", fail_fetch)

    result = scrape_url("https://example.com")

    assert result.website_url == "https://example.com"
    assert result.error == "request timed out"