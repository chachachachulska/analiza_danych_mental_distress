import logging

import duckdb
import pandas as pd
import statsmodels.api as sm
from duckdb import SQLExpression

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str):
        self.conn = duckdb.connect(db_path)

    def table(self, name: str) -> duckdb.DuckDBPyRelation:
        return self.conn.table(name)

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def perform_analysis(df: pd.DataFrame, target: str, features: list[str]):
    X, y = sm.add_constant(df[features].to_numpy()), df[target].to_numpy()
    model = sm.OLS(y, X)
    return model.fit()


def perform_query() -> pd.DataFrame:
    with Database("data/db.duckdb") as db:
        logger.info("Connected to data/db.duckdb")

        query = (
            db.table("social_media_usage_genz")
            .select(
                SQLExpression("screen_time_before_sleep"),
                SQLExpression("daily_usage_hours"),
                SQLExpression("mental_health_score"),
            )
            .limit(1000)
        )

        query.show()
        df = query.df()

        if df.empty:
            logger.warning("No data found")

        logger.info(f"Loaded {len(df)} rows")
        return df


def main():
    try:
        df = perform_query()
        model = perform_analysis(
            df,
            "mental_health_score",
            ["screen_time_before_sleep", "daily_usage_hours"],
        )
        print(model.summary())

    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
