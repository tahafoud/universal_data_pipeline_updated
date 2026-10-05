import pandas as pd

from src.ingestion.mongo_source import MongoDBSource


def test_make_dataframe_flattens_nested_documents_and_stringifies_id():
    class FakeObjectId:
        def __str__(self):
            return "abc123"

    df = MongoDBSource._make_dataframe([
        {"_id": FakeObjectId(), "name": "Ali", "address": {"city": "Sanaa"}},
    ])

    assert isinstance(df, pd.DataFrame)
    assert df.loc[0, "_id"] == "abc123"
    assert df.loc[0, "address.city"] == "Sanaa"
