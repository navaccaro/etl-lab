# ETL Lab

A hands-on data engineering project for building and operating a configuration-driven weather ETL pipeline with Python, PostgreSQL, Docker, and Apache Airflow.

The project is intended as a practical lab for modern data engineering patterns: configuration-driven ingestion, validation, idempotent loading, orchestration, automated testing, and CI.

## Current Architecture

```text
config/locations/*.yaml
        |
        v
load_locations()
        |
        v
Open-Meteo API
        |
        v
extract_weather(location)
        |
        +--> data/raw/*.json
        |
        v
transform_weather(payload, location)
        |
        v
load_weather(record)
        |
        v
PostgreSQL weather_observations
```

The same ETL components can run directly from Python or through Airflow. In Airflow, each enabled location becomes its own TaskGroup with an `extract -> transform -> load` chain.

## Key Features

- Configuration-driven weather locations using YAML
- JSON Schema and Pydantic validation
- Open-Meteo weather extraction
- Raw JSON payload preservation
- Data quality checks during transformation
- PostgreSQL loading with idempotent upserts on `(location_id, observed_at)`
- Apache Airflow 3 orchestration
- One Airflow TaskGroup per enabled location
- Retry behavior for Airflow tasks
- Pytest unit tests
- Ruff linting and formatting
- mypy static type checking
- GitHub Actions CI

## Repository Layout

```text
.
├── airflow/
│   └── dags/                  # Airflow DAGs
├── config/
│   ├── locations/             # Location YAML definitions
│   └── schemas/               # JSON Schema contracts
├── data/
│   └── raw/                   # Ignored raw API payloads
├── requirements/              # Runtime and development dependencies
├── scripts/
│   ├── add_location.py        # Location onboarding CLI
│   └── validate_locations.py  # Validate location configuration
├── tests/                     # Pytest suite
├── weather_etl/               # ETL package
├── docker-compose.postgres.yml
├── docker-compose.yml         # Full Airflow/PostgreSQL/Redis stack
├── Dockerfile
└── pyproject.toml
```

## Location Configuration

Locations live in `config/locations/`.

A location definition looks like:

```yaml
version: 1
location_id: forest-park-il
display_name: Forest Park, Illinois
latitude: 41.8795
longitude: -87.8137
timezone: America/Chicago
enabled: true
```

The filename must match the location ID:

```text
config/locations/forest-park-il.yaml
```

Location configuration is validated against the weather location JSON Schema and the `WeatherLocation` Pydantic model.

### Add a Location

Use the onboarding script rather than creating YAML manually:

```bash
python scripts/add_location.py \
  --id chicago-il \
  --name "Chicago, Illinois" \
  --latitude 41.8781 \
  --longitude -87.6298 \
  --timezone America/Chicago
```

Validate the complete configuration with:

```bash
python scripts/validate_locations.py
```

## Local Development

### Prerequisites

- Python 3.11+
- Docker Desktop with WSL2 integration when developing on Windows
- Git

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the project and development dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install -r requirements/dev.txt
```

Create your local environment file:

```bash
cp .env.example .env
```

## Run the ETL Directly

For lightweight Python development, start PostgreSQL:

```bash
docker compose -f docker-compose.postgres.yml up -d
```

Then run the pipeline:

```bash
python -m weather_etl.run_pipeline
```

The pipeline:

1. Loads every enabled location.
2. Requests current weather data from Open-Meteo.
3. Preserves the raw API response under `data/raw/`.
4. Transforms and validates the observation.
5. Upserts the observation into PostgreSQL.

Weather observations use `(location_id, observed_at)` as their unique key, allowing retries without creating duplicate observations.

## Run with Airflow

Build and start the full stack:

```bash
docker compose build
docker compose up -d
```

Check service health:

```bash
docker compose ps
```

Verify that Airflow imports the DAG successfully:

```bash
docker compose exec airflow-scheduler \
  airflow dags list-import-errors
```

The DAG is named:

```text
weather_etl_pipeline
```

Airflow is available locally at:

```text
http://localhost:8080
```

Each enabled location is represented as a TaskGroup:

```text
forest_park_il
    |
    +-- extract
    |
    +-- transform
    |
    +-- load
```

Additional enabled locations automatically create additional task groups without requiring DAG code changes.

## Quality Gates

Run the same checks enforced by CI:

```bash
python scripts/validate_locations.py
python -m pytest
ruff check .
ruff format --check .
mypy weather_etl scripts
```

GitHub Actions runs these checks on pushes to `main` and feature branches and on pull requests targeting `main`.

## Design Principles

### Configuration over code

Adding a weather location should not require changes to the ETL or DAG code. Locations are configuration consumed by the pipeline.

### Stable business keys

`location_id` is the stable identifier for a location. Human-readable names can change without changing the warehouse key.

### Idempotent loading

Weather observations are upserted using:

```text
(location_id, observed_at)
```

Rerunning a pipeline for the same observation therefore updates the existing record rather than creating a duplicate.

### Separation of orchestration and ETL logic

The extraction, transformation, and loading logic lives in the `weather_etl` package rather than inside the Airflow DAG. The same pipeline components can therefore be executed and tested independently of Airflow.

## Roadmap

Planned additions include:

- richer multi-location raw-data organization
- additional integration and database tests
- streamlined local Airflow resource usage
- dbt transformation and modeling
- metadata and lineage exploration with OpenMetadata
- additional observability and data-quality checks

## Current Status

The current milestone is a working configuration-driven weather ETL pipeline that has been exercised both directly in Python and through Apache Airflow, with PostgreSQL persistence and automated quality gates.