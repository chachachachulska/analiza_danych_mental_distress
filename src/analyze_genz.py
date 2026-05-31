import duckdb

con = duckdb.connect("data/db.duckdb")

# Mapping for PHQ-9 and GAD-7
val_map = {
    "Not at all": 0,
    "Several days": 1,
    "More than half of the days": 2,
    "Nearly every day": 3,
}


def calc_score(df, prefix, count):
    score = 0
    for i in range(1, count + 1):
        col = f"{prefix}_{i}"
        score += df[col].map(val_map).fillna(0)
    return score


df = con.execute("SELECT * FROM mental_health_survey").df()

# Convert birth year to age (survey taken in early 2022)
df["age"] = 2022 - df["year_1"]

# Filter for Gen Z (born 1997-2012, but minimum 18)
# Born 1997-2004 are 18-25 in 2022.
genz_df = df[(df["year_1"] >= 1997) & (df["year_1"] <= 2004)].copy()

print(f"Gen Z respondents in Prolific survey: {len(genz_df)}")

genz_df["phq9_score"] = calc_score(genz_df, "phq9", 9)
genz_df["gad7_score"] = calc_score(genz_df, "gad7", 7)

# Categorize
genz_df["moderate_depression"] = (genz_df["phq9_score"] >= 10).astype(int)
genz_df["moderate_anxiety"] = (genz_df["gad7_score"] >= 10).astype(int)

# Identify mobile users (iPhone, Android)
genz_df["is_mobile"] = (
    genz_df["BrowserInfo_Operating System"]
    .str.lower()
    .str.contains("iphone|android|ios", na=False)
).astype(int)

# Clean up demographics for regression
genz_df["is_female"] = (genz_df["sex"] == "Female").astype(int)
genz_df["is_student"] = (genz_df["fulltime"] == "Yes").astype(int)

# Save individual level data
con.register("genz_individual_view", genz_df)
con.execute(
    "CREATE OR REPLACE TABLE prolific_genz_individual AS SELECT * FROM genz_individual_view"
)

# Create a state summary table
con.execute(
    "CREATE OR REPLACE TABLE prolific_state_summary AS SELECT state_1 as state_name, AVG(phq9_score) as avg_phq9, AVG(gad7_score) as avg_gad7, AVG(moderate_depression) as depression_rate, AVG(is_mobile) as mobile_usage_rate, COUNT(*) as count FROM prolific_genz_individual GROUP BY state_1"
)

# Now handle CDC data
# Extract state from MMSANAME
cdc_df = con.execute("SELECT * FROM cdc_smart").df()
cdc_df["state"] = cdc_df["MMSANAME"].str.decode("latin1").str.extract(r",\s([A-Z]{2})")

# Filter for Gen Z (18-25)
cdc_genz = cdc_df[(cdc_df["_AGE80"] >= 18) & (cdc_df["_AGE80"] <= 25)].copy()

# MENTHLTH: 1-30 are days, 88 is 0. 77/99 are null.
cdc_genz["menthlth_days"] = cdc_genz["MENTHLTH"].replace(88, 0)
cdc_genz.loc[cdc_genz["menthlth_days"] > 30, "menthlth_days"] = None

# PHYSHLTH: 1-30 are days, 88 is 0. 77/99 are null.
cdc_genz["physhlth_days"] = cdc_genz["PHYSHLTH"].replace(88, 0)
cdc_genz.loc[cdc_genz["physhlth_days"] > 30, "physhlth_days"] = None

# SLEPTIM1: 1-24 are hours. 77/99 are null.
cdc_genz["sleep_hours"] = cdc_genz["SLEPTIM1"].copy()
cdc_genz.loc[cdc_genz["sleep_hours"] > 24, "sleep_hours"] = None

# _BMI5: BMI * 100.
cdc_genz["bmi"] = cdc_genz["_BMI5"] / 100.0

# _MENT14D: 3 is frequent distress (14+ days)
cdc_genz["frequent_distress"] = (cdc_genz["_MENT14D"] == 3).astype(int)

# INCOME3: 1-11 are categories. 77/99 are null.
cdc_genz["income_score"] = cdc_genz["INCOME3"].copy()
cdc_genz.loc[cdc_genz["income_score"] > 11, "income_score"] = None

con.register("cdc_genz_view", cdc_genz)
con.execute(
    "CREATE OR REPLACE TABLE cdc_state_summary AS SELECT state as state_code, AVG(menthlth_days) as avg_menthlth_days, AVG(physhlth_days) as avg_physhlth_days, AVG(sleep_hours) as avg_sleep_hours, AVG(bmi) as avg_bmi, AVG(income_score) as avg_income_score, STDDEV(income_score) as income_stddev, AVG(frequent_distress) as distress_rate, COUNT(*) as count FROM cdc_genz_view GROUP BY state"
)

print("Summaries created.")
con.close()
