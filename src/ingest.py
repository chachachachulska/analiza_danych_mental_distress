import os

import duckdb as db
import pandas as pd

con = db.connect("data/db.duckdb")


def ingest_parquet(table_name, path):
    print(f"Ingesting {table_name} from {path}...")
    if not os.path.exists(path):
        print(f"Warning: {path} not found.")
        return
    con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM '{path}'")


print("Ingesting CDC SMART 2022 data...")
# CDC was already parquet
ingest_parquet("cdc_smart", "data/cdc_smart_data_2022.parquet")

ingest_parquet("ipeds_counts", "data/ipeds_counts.parquet")
ingest_parquet("social_media_usage_genz", "data/social_media_usage_genz.parquet")
ingest_parquet("ipeds_hd", "data/ipeds_hd.parquet")
ingest_parquet("intro_dates", "data/intro_dates.parquet")
ingest_parquet("mental_health_survey", "data/mental_health_survey.parquet")
ingest_parquet("network_data", "data/network_data.parquet")
ingest_parquet("regions", "data/regions.parquet")

print("Ingestion complete.")
con.close()
