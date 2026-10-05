import pandas as pd


class ValidationEngine:
    def __init__(self, rules):
        self.rules = rules

    def validate(self, df, table):
        errors = []

        required = self.rules.get(
            "required_columns", {}
        ).get(table, [])

        for column in required:
            if column not in df.columns:
                errors.append({
                    "table": table,
                    "column": column,
                    "error": "missing_required_column",
                })

        for key, allowed in self.rules.get(
            "allowed_values", {}
        ).items():
            rule_table, column = key.split(".", 1)

            if rule_table != table or column not in df.columns:
                continue

            invalid = ~df[column].isin(allowed)

            for index in df.index[invalid]:
                errors.append({
                    "table": table,
                    "row": int(index),
                    "column": column,
                    "error": "invalid_allowed_value",
                    "value": str(df.loc[index, column]),
                })

        for key, limits in self.rules.get(
            "ranges", {}
        ).items():
            rule_table, column = key.split(".", 1)

            if rule_table != table or column not in df.columns:
                continue

            if "min" in limits:
                mask = df[column] < limits["min"]
                for index in df.index[mask]:
                    errors.append({
                        "table": table,
                        "row": int(index),
                        "column": column,
                        "error": "below_minimum",
                    })

            if "max" in limits:
                mask = df[column] > limits["max"]
                for index in df.index[mask]:
                    errors.append({
                        "table": table,
                        "row": int(index),
                        "column": column,
                        "error": "above_maximum",
                    })

        for key, pattern in self.rules.get(
            "regex", {}
        ).items():
            rule_table, column = key.split(".", 1)

            if rule_table != table or column not in df.columns:
                continue

            mask = ~df[column].astype(str).str.match(
                pattern, na=False
            )

            for index in df.index[mask]:
                errors.append({
                    "table": table,
                    "row": int(index),
                    "column": column,
                    "error": "regex_validation_failed",
                })

        return pd.DataFrame(errors)
