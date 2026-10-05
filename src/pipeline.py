import json
import os
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
from dotenv import load_dotenv

from src.ingestion.csv_source import CSVSource
from src.ingestion.api_source import APISource
from src.ingestion.web_source import WebSource
from src.ingestion.postgres_source import PostgreSQLSource
from src.ingestion.mongo_source import MongoDBSource
from src.schema.inspector import SchemaInspector
from src.schema.matcher import SchemaMatcher
from src.transform.cleaner import DataCleaner
from src.transform.normalizer import ColumnNormalizer
from src.validation.rules import ValidationEngine
from src.storage.sqlite_store import SQLiteStore
from src.storage.mongo_store import MongoStore


def load_config():
    with open("config/pipeline_config.json", encoding="utf-8") as f:
        return json.load(f)


def collect_sources(config):
    sources = []

    for path in config["sources"].get("csv", []):
        sources.append(CSVSource(path).read())

    for item in config["sources"].get("api", []):
        try:
            sources.append(
                APISource(item["name"], item["url"]).read()
            )
        except Exception as exc:
            print(f"[API] skipped {item['name']}: {exc}")

    for item in config["sources"].get("web", []):
        try:
            sources.append(
                WebSource(item["name"], item["url"]).read()
            )
        except Exception as exc:
            print(f"[WEB] skipped {item['name']}: {exc}")

    pg_cfg = config["sources"].get("postgresql", {})
    if pg_cfg.get("enabled"):
        postgres = PostgreSQLSource(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )
        sources.extend(
            postgres.read_all_tables(
                pg_cfg.get("schemas", ["public"])
            )
        )

    mongo_cfg = config["sources"].get("mongodb", {})
    if mongo_cfg.get("enabled"):
        mongo_source = MongoDBSource(
            uri=os.getenv(
                "MONGO_SOURCE_URI",
                "mongodb://localhost:27017/",
            ),
            database=os.getenv(
                "MONGO_SOURCE_DATABASE",
                mongo_cfg.get("database", "source_data"),
            ),
        )
        try:
            mongo_source.ping()
            collections = mongo_cfg.get("collections", [])
            loaded = mongo_source.read_all_collections(collections)
            sources.extend(loaded)
        finally:
            mongo_source.close()

    return sources


def group_similar_sources(items, threshold):
    groups = []

    for item in items:
        normalized = item.copy()
        normalized["data"] = ColumnNormalizer.normalize(
            item["data"]
        )

        placed = False

        for group in groups:
            score = SchemaMatcher.table_similarity(
                group[0]["data"].columns,
                normalized["data"].columns,
            )

            if score >= threshold:
                group.append(normalized)
                placed = True
                break

        if not placed:
            groups.append([normalized])

    return groups


def add_lineage(df, sources):
    df = df.copy()
    df["_ingested_at"] = datetime.now(timezone.utc)
    df["_source"] = ",".join(sorted(set(sources)))
    df["_pipeline_version"] = "1.0.0"
    return df


def main():
    load_dotenv()
    config = load_config()
    Path("data/processed").mkdir(parents=True, exist_ok=True)

    sources = collect_sources(config)
    print(f"[INGESTION] loaded {len(sources)} source tables")

    if not sources:
        raise RuntimeError("No source data was loaded.")

    schema = SchemaInspector.inspect_sources(sources)
    print("\n[SCHEMA]")
    print(schema.to_string(index=False))

    sqlite = SQLiteStore(config["sqlite_path"])
    sqlite.save_schema(schema)

    for item in sources:
        safe_name = f"raw_{item['source']}_{item['table']}"
        sqlite.save_raw(item["data"], safe_name)

    print("[RAW] stored in SQLite")

    groups = group_similar_sources(
        sources,
        config["matching"]["min_table_similarity"],
    )

    cleaner = DataCleaner(config["cleaning"])
    validator = ValidationEngine(config["validation"])

    mongo = MongoStore(
        os.getenv("MONGO_URI", "mongodb://localhost:27017/"),
        config["mongo_database"],
    )

    try:
        for group in groups:
            table_name = group[0]["table"]

            merged = pd.concat(
                [x["data"] for x in group],
                ignore_index=True,
                sort=False,
            )

            merged = add_lineage(
                merged,
                [x["source"] for x in group],
            )

            cleaned = cleaner.clean(merged)

            errors = validator.validate(
                cleaned,
                table_name,
            )

            if not errors.empty:
                error_path = (
                    f"data/processed/{table_name}_errors.csv"
                )
                errors.to_csv(error_path, index=False)
                print(
                    f"[VALIDATION] {table_name}: "
                    f"{len(errors)} errors"
                )

            mongo.save(cleaned, table_name)

            cleaned.to_csv(
                f"data/processed/{table_name}.csv",
                index=False,
            )

            print(
                f"[MONGO] {table_name}: "
                f"{len(cleaned)} records from "
                f"{len(group)} source table(s)"
            )
    finally:
        mongo.close()

    print("\nPipeline completed successfully.")


