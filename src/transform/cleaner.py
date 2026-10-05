import pandas as pd


class DataCleaner:
    def __init__(self, config):
        self.config = config

    def clean(self, df):
        df = df.copy()

        df.columns = (
            df.columns.astype(str)
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        if self.config.get("strip_strings", True):
            for column in df.select_dtypes(
                include=["object", "string"]
            ):
                df[column] = (
                    df[column].astype("string").str.strip()
                )

        if self.config.get("empty_strings_to_null", True):
            df = df.replace({
                "": pd.NA,
                "null": pd.NA,
                "NULL": pd.NA,
                "N/A": pd.NA,
                "n/a": pd.NA,
                "unknown": pd.NA,
                "Unknown": pd.NA,
                "not_available": pd.NA,
            })

        numeric_hints = {
            "id", "identifier", "customer_id", "order_id",
            "age", "amount", "price"
        }

        for column in df.columns:
            if column in numeric_hints:
                df[column] = pd.to_numeric(
                    df[column], errors="coerce"
                )

        for column in df.columns:
            if "date" in column or column.endswith("_at"):
                df[column] = pd.to_datetime(
                    df[column], errors="coerce"
                )

        if self.config.get("drop_duplicates", True):
            df = df.drop_duplicates()

        for column in df.columns:
            if pd.api.types.is_numeric_dtype(df[column]):
                value = df[column].median()
                if pd.notna(value):
                    df[column] = df[column].fillna(value)
            else:
                df[column] = df[column].fillna(
                    self.config.get("string_fill", "Unknown")
                )

        return df
