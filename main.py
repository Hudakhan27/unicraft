"""Command-line entry point for the company website scraper."""

import argparse
import csv
import json
from pathlib import Path

from app.scraper import scrape_url


def _fetch_urls_from_query(query: str, max_results: int = 5) -> list[str]:
    """Search query se seed URLs find karne ke liye (DuckDuckGo integration)."""
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                if "href" in r:
                    results.append(r["href"])
        return results
    except Exception as e:
        print(f"Error fetching search results: {e}")
        return []


def _write_results(results: list[dict], output: Path, output_format: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)

    if output_format == "csv":
        fields = ["company_name", "website_url", "emails", "phones", "tech_stack", "error"]
        with output.open("w", newline="", encoding="utf-8") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=fields)
            writer.writeheader()
            for result in results:
                writer.writerow(
                    {
                        **result,
                        "emails": "; ".join(result["emails"]),
                        "phones": "; ".join(result["phones"]),
                        "tech_stack": "; ".join(result["tech_stack"]),
                    }
                )
        return

    output.write_text(json.dumps(results, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract public company details from websites.")
    parser.add_argument("urls", nargs="*", help="One or more HTTP(S) website URLs")
    parser.add_argument("-q", "--query", help="Search query to discover companies (e.g., 'cloud startups in Europe')")
    parser.add_argument("-o", "--output", default="data/output.json", help="Output file path")
    parser.add_argument("--format", choices=("json", "csv"), default="json")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    args = parser.parse_args()

    target_urls = list(args.urls) if args.urls else []

    # Agar user ne --query / -q dia ho
    if args.query:
        print(f"Searching for query: '{args.query}'...")
        discovered_urls = _fetch_urls_from_query(args.query)
        target_urls.extend(discovered_urls)

    if not target_urls:
        parser.error("Please provide either seed URLs or a search query using --query / -q")

    results = [scrape_url(url, timeout=args.timeout).model_dump() for url in target_urls]
    output = Path(args.output)
    _write_results(results, output, args.format)
    print(f"Scraping completed. Results written to {output}")


if __name__ == "__main__":
    main()
