import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def main():
    con = duckdb.connect("data/db.duckdb")

    # 1. Prepare combined state-level data
    query = """
    WITH state_fb AS (
        SELECT
            h.STABBR as state_code,
            AVG(i.expansion_batch) as avg_fb_batch
        FROM intro_dates i
        JOIN ipeds_hd h ON i.unitid = h.UNITID
        GROUP BY h.STABBR
    )
    SELECT
        p.state_name,
        p.avg_phq9,
        p.depression_rate as prolific_depression_rate,
        p.mobile_usage_rate as prolific_mobile_rate,
        p.count as prolific_count,
        c.state_code,
        c.avg_menthlth_days,
        c.avg_physhlth_days,
        c.avg_sleep_hours,
        c.avg_income_score,
        c.distress_rate as cdc_distress_rate,
        c.count as cdc_count,
        r.Region,
        fb.avg_fb_batch
    FROM prolific_state_summary p
    JOIN regions r ON p.state_name = r.State
    JOIN cdc_state_summary c ON r."State Code" = c.state_code
    LEFT JOIN state_fb fb ON c.state_code = fb.state_code
    """
    df_state = con.execute(query).df()

    # Get individual level data for PHQ-9 by Device
    df_individual = con.execute(
        "SELECT phq9_score, is_mobile FROM prolific_genz_individual"
    ).df()

    con.close()

    sns.set_theme(style="whitegrid")
    palette = {"Midwest": "C0", "Northeast": "C1", "South": "C2", "West": "C3"}

    # --- Plot 1: State-Level Depression Rates: CDC vs Prolific ---
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=df_state,
        x="cdc_distress_rate",
        y="prolific_depression_rate",
        hue="Region",
        size="prolific_count",
        sizes=(20, 500),
        alpha=0.6,
        palette=palette,
    )
    plt.title("State-Level Depression Rates: CDC vs Prolific (Gen Z)")
    plt.xlabel("CDC Frequent Mental Distress Rate (14+ days)")
    plt.ylabel("Prolific PHQ-9 Moderate+ Depression Rate")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig("output/plot1_cdc_vs_prolific.png")
    plt.close()

    # --- Plot 2: Sleep Duration vs FB Batch & Mental Distress vs Physical Health ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    sns.scatterplot(
        data=df_state,
        x="avg_fb_batch",
        y="avg_sleep_hours",
        hue="Region",
        alpha=0.6,
        ax=ax1,
        palette=palette,
    )
    ax1.set_title("Sleep Duration vs FB Batch")
    ax1.set_xlabel("FB Expansion Batch (Lower = Earlier)")
    ax1.set_ylabel("Avg Sleep Hours")

    sns.scatterplot(
        data=df_state,
        x="avg_physhlth_days",
        y="cdc_distress_rate",
        hue="Region",
        alpha=0.6,
        ax=ax2,
        palette=palette,
    )
    ax2.set_title("Mental Distress vs Physical Health")
    ax2.set_xlabel("Avg Physical Health Days (Bad)")
    ax2.set_ylabel("Mental Distress Rate")

    plt.tight_layout()
    plt.savefig("output/plot2_sleep_phys.png")
    plt.close()

    # --- Plot 3: Depression Rate vs Facebook Expansion Batch (State Level) ---
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=df_state,
        x="avg_fb_batch",
        y="prolific_depression_rate",
        hue="Region",
        size="prolific_count",
        sizes=(20, 500),
        alpha=0.6,
        palette=palette,
    )
    plt.title("Depression Rate vs Facebook Expansion Batch (State Level)")
    plt.xlabel("Average Facebook Expansion Batch (Lower = Earlier)")
    plt.ylabel("Prolific PHQ-9 Moderate+ Depression Rate")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig("output/plot3_depression_fb.png")
    plt.close()

    # --- Plot 4: Mental Distress vs State Income (Colored by Mobile Usage) ---
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=df_state,
        x="avg_income_score",
        y="cdc_distress_rate",
        hue="prolific_mobile_rate",
        size="prolific_mobile_rate",
        sizes=(20, 200),
        alpha=0.8,
        palette="flare",
    )
    plt.title("Mental Distress vs. State Income (Colored by Mobile Usage)")
    plt.xlabel("Average State Income Category (CDC Gen Z)")
    plt.ylabel("CDC Frequent Mental Distress Rate")
    plt.legend(title="prolific_mobile_rate", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig("output/plot4_income_mobile.png")
    plt.close()

    # --- Plot 5: Platform Heritage vs Device Usage in Predicting Depression ---
    plt.figure(figsize=(10, 6))
    # This one is tricky. The image shows two series on the same plot.
    # Heritage Batch / Mobile Rate (Scaled)
    # It looks like they scaled mobile rate to be in a similar range as FB batch?
    # FB Batch is around 2-4. Mobile rate is 0-1.
    # If I multiply mobile rate by 10 or 20?
    # Let's look at the image 5. X-axis goes up to 35.
    # FB Batch is clustered around 2-4.
    # Mobile rate (scaled) is spread out up to 35. Maybe mobile_rate * 50?

    plt.scatter(
        df_state["avg_fb_batch"],
        df_state["prolific_depression_rate"],
        color="blue",
        alpha=0.5,
        label="FB Batch (Platform)",
    )
    plt.scatter(
        df_state["prolific_mobile_rate"] * 50,
        df_state["prolific_depression_rate"],
        color="red",
        alpha=0.5,
        label="Mobile Rate (Device) [Scaled]",
    )

    plt.title("Platform Heritage vs Device Usage in Predicting Depression")
    plt.xlabel("Heritage Batch / Mobile Rate (Scaled)")
    plt.ylabel("Depression Rate")
    plt.legend(loc="lower right")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("output/plot5_heritage_vs_device.png")
    plt.close()

    # --- Plot 6: Individual PHQ-9 by Device Type & CDC Mental Distress vs Mobile Usage Rate ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    sns.boxplot(data=df_individual, x="is_mobile", y="phq9_score", ax=ax1)
    ax1.set_xticklabels(["Desktop", "Mobile"])
    ax1.set_title("Individual PHQ-9 by Device Type")
    ax1.set_xlabel("is_mobile")
    ax1.set_ylabel("Depression Score (PHQ-9)")

    sns.regplot(data=df_state, x="prolific_mobile_rate", y="cdc_distress_rate", ax=ax2)
    ax2.set_title("CDC Mental Distress vs. Mobile Usage Rate")
    ax2.set_xlabel("State Mobile Usage Rate (Prolific Proxy)")
    ax2.set_ylabel("CDC Frequent Mental Distress Rate")

    plt.tight_layout()
    plt.savefig("output/plot6_individual_and_reg.png")
    plt.close()

    print("Visualizations generated in output/ directory.")

    print("Visualizations generated in output/ directory.")

if __name__ == "__main__":
    main()
