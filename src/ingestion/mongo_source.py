from __future__ import annotations

from typing import Any

import pandas as pd
from pymongo import MongoClient


class MongoDBSource:
    """Read MongoDB collections as pipeline source tables."""

    def __init__(self, uri: str, database: str, timeout_ms: int = 5000):
        self.uri = uri
        self.database_name = database
        self.client = MongoClient(uri, serverSelectionTimeoutMS=timeout_ms)
        self.db = self.client[database]

    def ping(self) -> None:
        self.client.admin.command("ping")

    def get_collections(self) -> list[str]:
        return sorted(self.db.list_collection_names())

    @staticmethod
    def _make_dataframe(documents: list[dict[str, Any]]) -> pd.DataFrame:
        if not documents:
            return pd.DataFrame()

        normalized = pd.json_normalize(documents, sep=".")

        # MongoDB ObjectId is not safely representable in SQLite/Pandas.
        # Keep the original identifier as a string field.
        if "_id" in normalized.columns:
            normalized["_id"] = normalized["_id"].map(str)

        return normalized

    def read_collection(self, collection: str) -> dict:
        documents = list(self.db[collection].find({}))
        return {
            "source": "mongodb",
            "table": collection,
            "database": self.database_name,
            "data": self._make_dataframe(documents),
        }

    def read_all_collections(self, collections: list[str] | None = None) -> list[dict]:
        selected = collections or self.get_collections()
        result = []

        for collection in selected:
            # Skip MongoDB internal collections if explicitly present.
            if collection.startswith("system."):
                continue
            result.append(self.read_collection(collection))

        return result

    def close(self) -> None:
        self.client.close()
