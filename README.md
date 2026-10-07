# Company Website Scraper

A small Python CLI that fetches user-provided company websites and extracts a page title or site name, public email addresses, phone numbers, and common technology indicators. It writes structured JSON by default and can also write CSV.

## Setup

Use Python 3.9 or newer:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

Pass one or more seed URLs. The scraper does not submit queries to Google or DuckDuckGo.

```powershell
python main.py https://example.com
python main.py https://example.com https://www.python.org --output data/companies.csv --format csv
```

The default output is `data/output.json`. The output directory is created automatically. Each result contains `company_name`, `website_url`, `emails`, `phones`, `tech_stack`, and `error`; failed URLs remain in the output with an error message.

Only scrape websites you are authorized to access. Respect each site's terms, robots policy, and rate limits. This starter makes one request per URL and does not crawl linked pages.

## Test

```powershell
python -m pytest
```

## Project layout

- `app/validator.py` validates absolute HTTP(S) URLs and fetches pages with a timeout and HTTP status checking.
- `app/scraper.py` coordinates fetching and extraction, converting request failures into result records.
- `app/extractor.py` extracts contact details, a company-name fallback, and technology hints into a Pydantic model.
- `main.py` provides the command-line interface and JSON/CSV writers.
- `tests/test_scraper.py` exercises validation, extraction, and network-error handling without live requests.