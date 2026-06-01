alias r := run

default: run

ingest:
    uv run python src/ingest.py

analyze:
    uv run python src/analyze_genz.py

visualize:
    uv run python src/generate_visualizations.py

run:
    uv run python src/ingest.py
    uv run python src/analyze_genz.py
    uv run python src/generate_visualizations.py
