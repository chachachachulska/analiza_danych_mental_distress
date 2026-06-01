from pathlib import Path

import duckdb as db

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"

con = db.connect(str(DATA_DIR / "db.duckdb"))


def ingest_parquet(table_name, path):
    parquet_path = DATA_DIR / path
    print(f"Ingesting {table_name} from {parquet_path}...")
    if not parquet_path.exists():
        print(f"Warning: {parquet_path} not found.")
        return
    con.execute(
        f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM '{parquet_path}'"
    )


print("Ingesting CDC SMART 2022 data...")
# CDC was already parquet
ingest_parquet("cdc_smart", "cdc_smart_data_2022.parquet")

ingest_parquet("ipeds_counts", "ipeds_counts.parquet")
ingest_parquet("social_media_usage_genz", "social_media_usage_genz.parquet")
ingest_parquet("ipeds_hd", "ipeds_hd.parquet")
ingest_parquet("intro_dates", "intro_dates.parquet")
ingest_parquet("mental_health_survey", "mental_health_survey.parquet")
ingest_parquet("network_data", "network_data.parquet")
ingest_parquet("regions", "regions.parquet")

print("Ingestion complete.")
con.close()
