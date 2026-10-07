"""Command-line entry point for the company website scraper."""

import argparse
import csv
import json
from pathlib import Path

from app.scraper import scrape_url


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
    parser.add_argument("urls", nargs="+", help="One or more HTTP(S) website URLs")
    parser.add_argument("-o", "--output", default="data/output.json", help="Output file path")
    parser.add_argument("--format", choices=("json", "csv"), default="json")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    args = parser.parse_args()

    results = [scrape_url(url, timeout=args.timeout).model_dump() for url in args.urls]
    output = Path(args.output)
    _write_results(results, output, args.format)
    print(f"Scraping completed. Results written to {output}")


if __name__ == "__main__":
    main()