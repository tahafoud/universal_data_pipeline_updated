import pandas as pd
from src.transform.cleaner import DataCleaner


def test_cleaning():
    df = pd.DataFrame({
        "age": ["20", "not_available", "20"],
        "name": [" Ali ", "Sara", " Ali "],
    })

    cleaner = DataCleaner({
        "drop_duplicates": True,
        "strip_strings": True,
        "empty_strings_to_null": True,
        "string_fill": "Unknown",
    })

    result = cleaner.clean(df)

    assert len(result) == 2
