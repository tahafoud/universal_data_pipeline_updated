from src.schema.matcher import SchemaMatcher


class ColumnNormalizer:
    @staticmethod
    def normalize(df):
        return df.rename(
            columns=SchemaMatcher.column_mapping(df.columns)
        )
