import pandas as pd
import psycopg


class PostgreSQLSource:
    def __init__(self, host, port, database, user, password):
        self.connection_args = {
            "host": host,
            "port": port,
            "dbname": database,
            "user": user,
            "password": password,
        }

    def get_tables(self, schemas=None):
        schemas = schemas or ["public"]
        query = """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
          AND table_schema = ANY(%s)
        ORDER BY table_schema, table_name
        """

        with psycopg.connect(**self.connection_args) as conn:
            return pd.read_sql_query(query, conn, params=(schemas,))

    def get_columns(self, schema, table):
        query = """
        SELECT table_schema, table_name, column_name,
               data_type, is_nullable, ordinal_position
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
        """

        with psycopg.connect(**self.connection_args) as conn:
            return pd.read_sql_query(
                query, conn, params=(schema, table)
            )

    def read_table(self, schema, table):
        query = f'SELECT * FROM "{schema}"."{table}"'

        with psycopg.connect(**self.connection_args) as conn:
            df = pd.read_sql_query(query, conn)

        return {
            "source": "postgresql",
            "table": table,
            "schema": schema,
            "data": df,
        }

    def read_all_tables(self, schemas=None):
        result = []
        tables = self.get_tables(schemas)

        for row in tables.itertuples(index=False):
            result.append(
                self.read_table(
                    row.table_schema,
                    row.table_name,
                )
            )

        return result
