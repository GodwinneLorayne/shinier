# Contributing

## Updating dependencies

To update dependencies, run the following commands:

- `bin/hatch run dev:uv pip compile --no-deps --output-file requirements.txt pyproject.toml`
- `bin/hatch run dev:uv pip compile --no-deps --constraint requirements.txt --output-file dev-requirements.txt --extra dev
 pyproject.toml`
