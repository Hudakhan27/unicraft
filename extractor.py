"""Extract company contact details and technology hints from HTML."""

import re
from typing import Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from pydantic import BaseModel, Field


EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"(?<!\w)\+?\d[\d().\s-]{7,}\d(?!\w)")

TECH_MARKERS = {
    "React": ("react", "react-dom"),
    "Next.js": ("_next/", "nextjs"),
    "Vue.js": ("vue",),
    "Angular": ("angular",),
    "WordPress": ("wp-content", "wp-includes"),
    "Shopify": ("cdn.shopify.com", "shopify"),
    "jQuery": ("jquery",),
    "Bootstrap": ("bootstrap",),
    "Tailwind CSS": ("tailwind",),
}


class CompanyData(BaseModel):
    company_name: str = "N/A"
    website_url: str
    emails: list[str] = Field(default_factory=list)
    phones: list[str] = Field(default_factory=list)
    tech_stack: list[str] = Field(default_factory=list)
    error: Optional[str] = None


def _company_name(soup: BeautifulSoup) -> str:
    for selector, attribute in (
        ('meta[property="og:site_name"]', "content"),
        ('meta[name="application-name"]', "content"),
    ):
        tag = soup.select_one(selector)
        if tag and tag.get(attribute):
            return tag[attribute].strip()

    if soup.title:
        title = soup.title.get_text(" ", strip=True)
        if title:
            return title

    heading = soup.find("h1")
    return heading.get_text(" ", strip=True) if heading else "N/A"


def _unique_matches(values: list[str], limit: int) -> list[str]:
    return list(dict.fromkeys(value.strip() for value in values if value.strip()))[:limit]


def _tech_stack(soup: BeautifulSoup, page_url: str) -> list[str]:
    signals = [page_url]
    signals.extend(str(value) for tag in soup.find_all(True) for value in tag.attrs.values())
    searchable = " ".join(signals).lower()
    return [
        technology
        for technology, markers in TECH_MARKERS.items()
        if any(marker in searchable for marker in markers)
    ]


def extract_company_data(html: str, url: str, limit: int = 3) -> CompanyData:
    """Extract a small set of public company details from an HTML document."""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    email_values = EMAIL_PATTERN.findall(text)
    email_values.extend(
        link.get("href", "").removeprefix("mailto:").split("?", 1)[0]
        for link in soup.select('a[href^="mailto:"]')
    )
    phone_values = PHONE_PATTERN.findall(text)
    phone_values.extend(
        link.get("href", "").removeprefix("tel:")
        for link in soup.select('a[href^="tel:"]')
    )

    return CompanyData(
        company_name=_company_name(soup),
        website_url=url,
        emails=_unique_matches(email_values, limit),
        phones=_unique_matches(phone_values, limit),
        tech_stack=_tech_stack(soup, url),
    )


def extract_company_name_from_url(url: str) -> str:
    """Provide a hostname fallback when a page has no identifiable name."""
    return urlparse(url).hostname or "N/A"