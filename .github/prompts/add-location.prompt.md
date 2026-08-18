---
mode: agent
description: Add a new weather location through the repository's validated onboarding workflow.
---

Add a new weather location to this repository.

Use the `add-weather-location` skill and follow all repository instructions in `.github/copilot-instructions.md`.

Required inputs:

- location ID
- display name
- latitude
- longitude
- IANA timezone

Use only the supported onboarding command:

`python scripts/add_location.py`

Do not manually create or edit the location YAML file.

After creating the location:

1. Run `python scripts/validate_locations.py`
2. Run `python -m pytest`
3. Run `git diff --check`
4. Inspect `git diff`

Do not modify DAG code, ETL code, validation logic, schemas, or unrelated files.

If any required location input is missing, ask for it rather than guessing.

If any validation or test fails, stop and report the failure. Do not weaken validation or tests to make the change pass.

At completion, report:

- location ID
- created file
- latitude/longitude
- timezone
- validation result
- test result
- any unexpected changed files