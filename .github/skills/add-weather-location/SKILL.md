---
name: add-weather-location
description: Safely add a new location to the configuration-driven weather ETL pipeline.
---

# Add Weather Location

Use this skill when the user asks to add a weather location.

## Objective

Add exactly one location through the repository's supported configuration workflow without modifying application or DAG code.

## Required inputs

Before performing the operation, the following values must be known:

- location ID
- display name
- latitude
- longitude
- IANA timezone

Do not guess missing required values.

If required information is missing, ask for it rather than inventing it.

## Procedure

1. Read `.github/copilot-instructions.md`.

2. Confirm the requested `location_id` follows lowercase kebab-case.

3. Check `config/locations/` for an existing configuration with the same ID.

4. Use the supported command:

   `python scripts/add_location.py --id <id> --name "<name>" --latitude <latitude> --longitude <longitude> --timezone <timezone>`

5. Do not manually create the YAML file.

6. Run:

   `python scripts/validate_locations.py`

7. Run:

   `python -m pytest`

8. Run:

   `git diff --check`

9. Inspect `git diff`.

10. Confirm that the location addition changed only the expected location configuration file.

## Prohibited actions

Do not:

- edit DAG code
- edit extract, transform, or load code
- edit the location schema
- edit validation logic
- weaken or remove tests
- manually create the location YAML
- overwrite an existing location
- add unsupported configuration fields
- modify unrelated files
- bypass a failing validation

## Failure behavior

If any step fails:

1. Stop the onboarding operation.
2. Preserve existing valid configuration.
3. Do not weaken validation to make the change pass.
4. Report the failing command and error.
5. Explain what input or repository change is required to continue.

## Success criteria

The task succeeds only when:

- one new location configuration exists
- the filename matches the location ID
- configuration validation passes
- all tests pass
- `git diff --check` passes
- no application or DAG code changed

## Completion report

Report:

- location ID
- created configuration file
- latitude and longitude
- timezone
- configuration validation result
- test result
- unexpected files changed, if any