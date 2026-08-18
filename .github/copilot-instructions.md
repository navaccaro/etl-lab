# Weather ETL Repository Instructions

## Architecture

This repository implements a configuration-driven weather ETL pipeline.

Location definitions are configuration, not application code.

The supported location onboarding interface is:

`python scripts/add_location.py`

## Non-negotiable rules

- Never hardcode location definitions in Python.
- Do not modify DAG code to add, update, disable, or remove a location.
- Do not modify extract, transform, or load code for a location-specific request.
- Location configuration files belong only in `config/locations/`.
- Do not manually create a location YAML file when `scripts/add_location.py` can perform the operation.
- Never overwrite an existing location configuration.
- Never bypass schema or application validation.
- Never invent configuration fields.
- Do not guess required location data.
- Do not modify the location schema unless the task explicitly requires a schema change.
- Do not modify unrelated files.

## Location contract

Location files must conform to:

`config/schemas/weather-location.schema.json`

Filenames must exactly match:

`<location_id>.yaml`

`location_id` must use lowercase kebab-case.

Example:

`forest-park-il.yaml`

must contain:

`location_id: forest-park-il`

## Adding a location

Use:

`python scripts/add_location.py`

Required inputs are:

- location ID
- display name
- latitude
- longitude
- timezone

The add-location operation validates the complete location configuration set and rolls back the new file if validation fails.

Do not bypass this operation by manually creating YAML.

## Validation

After any location configuration change, run:

`python scripts/validate_locations.py`

Then run:

`python -m pytest`

All checks must pass before the change is considered complete.

## Failure behavior

If any command, validation, or test fails:

1. Stop.
2. Do not work around the validation.
3. Do not weaken tests, schemas, or validation rules.
4. Report the failure and its cause.
5. Leave the repository in a valid state.

## Definition of done

A location onboarding task is complete only when:

- the location was created through the supported onboarding interface
- configuration validation passes
- the full test suite passes
- no unrelated files changed
- DAG and ETL application code were not modified
- the created configuration file and location ID are reported