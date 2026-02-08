# Broken Access Control Scanner
Broken Access Control Scanner is an AI command line tool to detect broken access control vulnerabilities in source code using Anthropic's Claude AI.

## Installation
Releases are made available on PyPi.
The recommended installation method is via `pip`:

```
pip install broken-access-control-scanner
```

## Usage

```
python -m broken_access_control_scanner <source_file> --data-model "<data_model_description>"
```

Requires `ANTHROPIC_API_KEY` environment variable to be set.

### Arguments

- `source_file`: Path to a source code file containing endpoints
- `--data-model`, `-d`: Description of the data model and context for the endpoints (required)
- `--model`, `-m`: Anthropic model to use (default: `claude-sonnet-4-20250514`)

### Example

```bash
python -m broken_access_control_scanner api.py \
    --data-model "REST API with User and Document models. Users should only access their own profiles."
```

### Output Example

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Endpoint                  ┃  Severity  ┃ Description                      ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ /api/users/{id}/profile   │    NONE    │ Proper authorization check       │
│ /api/documents/{id}       │  CRITICAL  │ No authentication or auth check  │
└───────────────────────────┴────────────┴──────────────────────────────────┘
```

## Severity Levels

- **NONE**: No access control issues found
- **LOW**: Minor issues, unlikely to be exploitable
- **MEDIUM**: Access control weakness that could be exploited under certain conditions
- **HIGH**: Clear access control vulnerability that can likely be exploited
- **CRITICAL**: Severe access control vulnerability with high impact, easily exploitable

