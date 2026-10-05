import json
import pandas as pd


class SchemaInspector:

    @staticmethod
    def _hashable_value(value):
        if isinstance(value, (dict, list, set, tuple)):
            try:
                return json.dumps(
                    value,
                    sort_keys=True,
                    ensure_ascii=False,
                    default=str
                )
            except Exception:
                return str(value)

        return value

    @staticmethod
    def inspect_dataframe(df, source, table):
        rows = []

        for position, column in enumerate(df.columns):
            series = df[column]

            safe_series = series.map(
                SchemaInspector._hashable_value
            )

            rows.append({
                "source": source,
                "table": table,
                "column": column,
                "pandas_dtype": str(series.dtype),
                "nullable": bool(series.isna().any()),
                "null_count": int(series.isna().sum()),
                "unique_count": int(safe_series.nunique(dropna=True)),
                "position": position,
            })

        return rows

    @staticmethod
    def inspect_sources(sources):
        rows = []

        for item in sources:
            rows.extend(
                SchemaInspector.inspect_dataframe(
                    item["data"],
                    item["source"],
                    item["table"]
                )
            )

        return pd.DataFrame(rows)