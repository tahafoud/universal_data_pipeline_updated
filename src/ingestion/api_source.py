import requests
import pandas as pd


class APISource:
    def __init__(self, name: str, url: str, timeout: int = 30):
        self.name = name
        self.url = url
        self.timeout = timeout

    def read(self) -> dict:
        response = requests.get(
            self.url,
            timeout=self.timeout,
            headers={"User-Agent": "UniversalDataPipeline/1.0"},
        )
        response.raise_for_status()
        payload = response.json()

        if isinstance(payload, list):
            records = payload
        elif isinstance(payload, dict):
            records = next(
                (value for value in payload.values()
                 if isinstance(value, list)),
                [payload],
            )
        else:
            raise ValueError("Unsupported API response format")

        return {
            "source": "api",
            "table": self.name,
            "data": pd.json_normalize(records),
        }
