# Mental Health Gen Z Analysis

This project investigates state-level patterns in Gen Z mental-health outcomes in the United States. It combines survey microdata, public-health data, social-media rollout history, college metadata, and Census region mappings to test whether youth distress is better explained by structural context than by a simple standalone "smartphone effect."

## Project Topic

The topic of this project is the mental health of Generation Z in the United States, with a focus on how depression, anxiety, and frequent mental distress vary across states and regions. The project connects individual survey responses with state-level public-health indicators to compare what different data sources reveal about the same broad problem.

The central motivation is that public discussions about Gen Z mental health often focus heavily on smartphones and social media. This project treats that explanation as one part of a broader system rather than as the only possible cause. It asks whether mental-health outcomes are also connected to regional context, physical-health conditions, sleep, income patterns, and historical differences in social-media exposure.

Because the analysis works mostly at the state level, the project is designed to identify patterns and generate hypotheses. It does not claim that one variable directly causes another at the individual level. Instead, it compares several possible explanations and evaluates which ones remain meaningful when they are considered together.

## Research Thesis

Working thesis:

> The spatial distribution of youth distress: assessing structural predictors of Gen Z mental health across regional socioeconomic landscapes.

The analysis treats device use and social-media history as contextual predictors, not as direct proof of individual-level causality. The Facebook rollout variable is a historical proxy for early social-media penetration in each state's college ecosystem. It should not be interpreted as evidence that today's Gen Z respondents personally adopted Facebook earlier.

## Project Requirements Covered

The attached scoring rubric emphasizes presentation readiness, multiple datasets, cleaning documentation, visualizations, statistical methods, Markdown explanation, code quality, and feedback implementation. This repository addresses those requirements as follows:

| Requirement | Where it is covered |
| --- | --- |
| Presentation-ready project | Research framing, findings, reproducible workflow, and output chart inventory are documented in this README. |
| At least three datasets | The project uses CDC SMART 2022, Prolific survey data, Facebook introduction dates, IPEDS institution metadata, Census regions, and supporting social/network datasets. |
| Cleaning process and summary | `src/analyze_genz.py` documents Gen Z filtering, PHQ-9/GAD-7 scoring, CDC missing-code handling, mobile-device detection, and state aggregation. |
| At least five visualizations | `src/generate_visualizations.py` produces six core plots; `notebook.ipynb` adds two robustness plots. |
| Correct and readable charts | Charts use labeled axes, titles, regional color coding, point sizing, boxplots, and regression plots where appropriate. |
| Five questions asked of the data | The questions are listed in the "Research Questions" section below. |
| Statistical methods | The notebook uses correlation checks, OLS regression, multivariable controls, p-values, and robustness comparisons. |
| Markdown explanation | The README and notebook Markdown explain the research logic, data pipeline, findings, and limitations. |
| Commented code | Core scripts include comments around scoring, filtering, cleaning, and plot intent. |
| Feedback and code variety | The current version expands beyond simple plots by adding DuckDB ingestion, derived tables, state joins, regression, individual-level comparison, and robustness analysis. |

## Research Questions

1. Do CDC frequent mental distress rates and Prolific PHQ-9 depression rates show similar state-level patterns for Gen Z?
2. Are mental-health outcomes different across US Census regions?
3. Is mobile-device usage associated with higher depression or distress after accounting for state context?
4. Does historical Facebook college rollout timing correlate with current Gen Z depression rates at the state level?
5. Do socioeconomic and physical-health variables, especially income variation, sleep, and bad physical-health days, explain more of the state-level distress pattern than device usage alone?

## Data Sources

Local source files live under `data/`, which is ignored by Git because the files are large and may include restricted survey data.

| Source file | Role in the analysis |
| --- | --- |
| `data/cdc_smart_data_2022.parquet` | CDC SMART 2022 public-health data for mental-health days, physical-health days, sleep, BMI, income, and frequent mental distress. |
| `data/mental_health_survey.parquet` | Prolific respondent-level survey data with PHQ-9, GAD-7, demographics, state, and browser/device metadata. |
| `data/intro_dates.parquet` | College-level Facebook introduction timing and expansion batches from 2004-2005. |
| `data/ipeds_hd.parquet` | Institution metadata used to map colleges to states. |
| `data/regions.parquet` | US Census state-to-region and division mapping. |
| `data/social_media_usage_genz.parquet` | Supporting Gen Z social-media usage data loaded for broader project context. |
| `data/network_data.parquet` | Supporting network data loaded during ingestion for broader project context. |

## Data Pipeline

1. `src/ingest.py` loads local Parquet files into `data/db.duckdb`.
2. `src/analyze_genz.py` creates cleaned and derived tables:
   - `prolific_genz_individual`
   - `prolific_state_summary`
   - `cdc_state_summary`
3. `src/generate_visualizations.py` joins the derived summaries with region, IPEDS, and Facebook rollout data to create visual outputs in `output/`.
4. `notebook.ipynb` runs exploratory robustness checks and regression models.

## Cleaning and Feature Engineering

The core cleaning steps are:

- Gen Z filter: Prolific respondents are limited to birth years 1997-2004, corresponding to ages 18-25 in 2022.
- PHQ-9 and GAD-7 scoring: survey response labels are mapped to numeric values from 0 to 3 and summed into depression and anxiety scores.
- Clinical threshold flags: moderate depression and anxiety are defined with score cutoffs of 10 or higher.
- Mobile proxy: browser operating-system metadata is converted into an `is_mobile` indicator for iPhone, Android, and iOS devices.
- CDC age filter: CDC SMART records are limited to ages 18-25.
- CDC missing-code handling: special values such as 77, 88, and 99 are converted according to CDC coding conventions, with valid values retained for mental-health days, physical-health days, sleep, BMI, and income.
- State aggregation: individual-level and CDC records are summarized to state-level rates and averages for cross-source comparison.
- Facebook rollout mapping: college-level rollout batches are joined through IPEDS state metadata and averaged by state.

## Visualizations

The scripted pipeline creates six core figures:

| Output | Question addressed |
| --- | --- |
| `output/plot1_cdc_vs_prolific.png` | Compares CDC frequent distress with Prolific moderate depression by state. |
| `output/plot2_sleep_phys.png` | Shows sleep versus Facebook rollout timing and mental distress versus bad physical-health days. |
| `output/plot3_depression_fb.png` | Tests whether earlier Facebook expansion states show different depression rates. |
| `output/plot4_income_mobile.png` | Compares mental distress with state income while visualizing mobile usage. |
| `output/plot5_heritage_vs_device.png` | Contrasts platform-history and device-use proxies against depression rates. |
| `output/plot6_individual_and_reg.png` | Shows individual PHQ-9 by device type and a state-level mobile/distress regression plot. |

The notebook adds:

- `output/depression_correlation.png`
- `output/inequality_stress_test.png`

## Current Findings

- Regional differences appear in CDC frequent mental distress rates, with the South showing higher average distress and the Northeast lower average distress in the current analysis.
- Prolific PHQ-9 depression rates are compared with CDC frequent mental distress rates to check whether both sources show similar state-level patterns.
- Mobile/device usage shows some association with distress in simple plots, but regression results suggest it is intertwined with economic variables.
- In the current robustness notebook, state-level income inequality remains statistically significant in the full model, while mobile usage does not.
- Physical-health measures, including bad physical-health days and sleep duration, are included as contextual modifiers rather than treated as purely digital effects.

These findings are exploratory and state-level. They support hypothesis generation, not individual-level causal claims.

## Statistical Methods

The project uses:

- descriptive aggregation by state and Census region;
- scatterplots and boxplots for exploratory comparison;
- correlation-style cross-source validation between CDC and Prolific mental-health indicators;
- OLS regression with `statsmodels`;
- multivariable regression controls for mobile usage, average income, and income variation;
- p-value checks to compare whether digital-use or structural variables remain significant in full models.

## Setup and Replication

### Prerequisites

- Python 3.12+
- `uv` for dependency management

### Steps

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Prepare local data files under `data/`.

   Download `data.zip` from Google Drive:

   ```text
   https://drive.google.com/file/d/1RnOdinoVUZHnU4pREKmF0kVx8k8TMjxy
   ```

   Unzip it into the project `data/` directory. The current ingestion script expects files such as:

   ```text
   data/cdc_smart_data_2022.parquet
   data/mental_health_survey.parquet
   data/intro_dates.parquet
   data/ipeds_hd.parquet
   data/regions.parquet
   data/social_media_usage_genz.parquet
   data/network_data.parquet
   ```

3. Ingest data into DuckDB:

   ```bash
   uv run python src/ingest.py
   ```

4. Create cleaned Gen Z analysis tables:

   ```bash
   uv run python src/analyze_genz.py
   ```

5. Generate the core visualizations:

   ```bash
   uv run python src/generate_visualizations.py
   ```

6. Open `notebook.ipynb` for regression and robustness checks.

## Project Structure

```text
.
├── README.md
├── notebook.ipynb
├── pyproject.toml
├── src/
│   ├── ingest.py
│   ├── analyze_genz.py
│   └── generate_visualizations.py
├── queries/
│   └── thesis.sql
├── data/
│   └── local source data and generated DuckDB database, ignored by Git
└── output/
    └── generated plots, ignored by Git
```

## Limitations

- Most results are state-level, so they should not be interpreted as individual-level causal estimates.
- The Prolific survey sample may not be representative of all Gen Z residents in each state.
- Mobile usage is inferred from browser metadata, which is a proxy for survey-taking device rather than total daily device exposure.
- Facebook rollout timing is a historical state-level context variable, not a direct exposure measure for current respondents.
- CDC SMART and Prolific use different mental-health measures, so cross-source comparisons are approximate validation checks rather than identical measurements.
