import requests
import pandas as pd
from bs4 import BeautifulSoup


class WebSource:
    def __init__(self, name: str, url: str, timeout: int = 30):
        self.name = name
        self.url = url
        self.timeout = timeout

    def read(self) -> dict:
        response = requests.get(
            self.url,
            timeout=self.timeout,
            headers={"User-Agent": "Mozilla/5.0 UniversalDataPipeline"},
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        rows = []

        for item in soup.select("article.product_pod"):
            title = item.select_one("h3 a")
            price = item.select_one(".price_color")
            availability = item.select_one(".availability")

            rows.append({
                "name": title.get("title") if title else None,
                "price": price.get_text(strip=True) if price else None,
                "availability": availability.get_text(" ", strip=True)
                if availability else None,
            })

        return {
            "source": "web",
            "table": self.name,
            "data": pd.DataFrame(rows),
        }
