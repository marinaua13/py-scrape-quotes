import csv
import requests
from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass
from typing import List


BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: List[str]


def parse_single_quote(quote_element: Tag) -> Quote:
    text = quote_element.select_one(".text").get_text()
    author = quote_element.select_one(".author").get_text()
    tags = [tag.get_text() for tag in quote_element.select("a.tag")]
    return Quote(text=text, author=author, tags=tags)


def parse_quotes_from_page(page_url: str) -> List[Quote]:
    response = requests.get(page_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    quote_elements = soup.find_all("div", class_="quote")
    return [
        parse_single_quote(
            quote_element
        )
        for quote_element in quote_elements
    ]


def get_all_quotes() -> List[Quote]:
    all_quotes = []
    page_url = "/page/1"

    while page_url:
        quotes = parse_quotes_from_page(BASE_URL + page_url)
        all_quotes.extend(quotes)

        response = requests.get(BASE_URL + page_url)
        soup = BeautifulSoup(response.text, "html.parser")
        next_page = soup.select_one("li.next > a")
        page_url = next_page["href"] if next_page else None

    return all_quotes


def main(output_csv_path: str) -> None:
    all_quotes = get_all_quotes()

    with open(
            output_csv_path,
            mode="w",
            newline="",
            encoding="utf-8"
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["text", "author", "tags"])
        for quote in all_quotes:
            formatted_tags = str(quote.tags)
            writer.writerow([quote.text, quote.author, formatted_tags])


if __name__ == "__main__":
    main("quotes.csv")
