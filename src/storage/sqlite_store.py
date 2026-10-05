import json
import sqlite3
from pathlib import Path

import pandas as pd


class SQLiteStore:
    def __init__(self, path):
        self.path = Path(path)

        # إنشاء مجلد قاعدة البيانات تلقائيًا
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _serialize_value(value):
        """
        SQLite لا يدعم list/dict مباشرة.
        نحول القيم المعقدة إلى JSON string.
        """

        if isinstance(value, (list, dict, tuple, set)):
            return json.dumps(
                value,
                ensure_ascii=False,
                default=str
            )

        return value

    def save_schema(self, schema):
        with sqlite3.connect(str(self.path)) as conn:
            schema.to_sql(
                "schema",
                conn,
                if_exists="replace",
                index=False
            )

    def save_raw(self, df, table_name):
        """
        حفظ البيانات الخام في SQLite.

        القيم البسيطة:
            int
            float
            str
            datetime

        تبقى كما هي.

        القيم المعقدة:
            list
            dict
            tuple
            set

        يتم تحويلها إلى JSON.
        """

        safe_df = df.copy()

        for column in safe_df.columns:
            safe_df[column] = safe_df[column].map(
                self._serialize_value
            )

        with sqlite3.connect(str(self.path)) as conn:
            safe_df.to_sql(
                table_name,
                conn,
                if_exists="replace",
                index=False
            )