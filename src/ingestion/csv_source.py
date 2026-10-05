from pathlib import Path
import pandas as pd


class CSVSource:
    def __init__(self, path: str):
        self.path = Path(path)

    def read(self) -> dict:
        return {
            "source": "csv",
            "table": self.path.stem,
            "data": pd.read_csv(self.path),
        }
