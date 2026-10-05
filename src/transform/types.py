import pandas as pd


def cast_types(df, type_contract):
    df = df.copy()

    for column, target_type in type_contract.items():
        if column not in df.columns:
            continue

        if target_type == "integer":
            df[column] = pd.to_numeric(
                df[column], errors="coerce"
            ).astype("Int64")
        elif target_type == "float":
            df[column] = pd.to_numeric(
                df[column], errors="coerce"
            ).astype("Float64")
        elif target_type == "string":
            df[column] = df[column].astype("string")
        elif target_type == "datetime":
            df[column] = pd.to_datetime(
                df[column], errors="coerce"
            )
        elif target_type == "boolean":
            df[column] = df[column].astype("boolean")

    return df
