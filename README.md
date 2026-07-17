# anota-api-python · Official Python client for the [anota](https://anota.cloud) API

**[Léeme en español](README.es.md)** · [Interactive API reference](https://anota.cloud/developers) · [All SDKs](https://github.com/anotacloud/anota-api)

![CI](https://github.com/anotacloud/anota-api-python/actions/workflows/ci.yml/badge.svg)

Create and publish forms, edit fields and conditional logic, read and write
submissions, and wire webhooks — everything the anota REST API can do, from Python.

The client is dependency-free (Python standard library only) and thin: responses
come back as ordinary Python dicts and lists, so you are never fighting rigid
model classes.

## Install

```bash
pip install anota-api
```

The package is published to [PyPI](https://pypi.org/project/anota-api/) on each GitHub release, so `pip install anota-api` becomes available once the first release publish has run. Until then, install straight from the repository:

```bash
pip install git+https://github.com/anotacloud/anota-api-python.git
```

Or download the [ZIP](https://github.com/anotacloud/anota-api-python/archive/refs/heads/main.zip) / [Tarball](https://github.com/anotacloud/anota-api-python/archive/refs/heads/main.tar.gz) and add `src/` to your path.

Requires Python 3.9+.

## Quickstart

```python
import os
from anota_api import AnotaClient

client = AnotaClient(api_key=os.environ["ANOTA_API_KEY"])

form = client.create_form(
    title="Contact us",
    fields=[{"type": "text", "label": "Name", "required": True}],
)
client.publish_form(form["id"])
client.create_submission(form["id"], {"Name": "Ada"})

print(client.list_submissions(form["id"]))
```

A full runnable script lives in [`examples/end_to_end.py`](examples/end_to_end.py).

## Authentication

Create an API key in your workspace at https://anota.cloud/api-keys and pass it to the
client. Keys look like `anota_sk_…` and also power the Claude MCP connector.

```python
client = AnotaClient(api_key="anota_sk_…")
# point at a different environment if needed:
client = AnotaClient(api_key="anota_sk_…", base_url="https://anota.cloud/api/v1")
```

## All methods

Every method returns the parsed JSON response (a `dict`, `list`, or `None` for empty bodies).

| # | Method | HTTP |
|---|---|---|
| 1 | `list_forms()` | `GET /forms` |
| 2 | `create_form(title, fields, description=None)` | `POST /forms` |
| 3 | `get_form(form_id)` | `GET /forms/{form_id}` |
| 4 | `add_fields(form_id, fields)` | `POST /forms/{form_id}/fields` |
| 5 | `edit_field(form_id, field_id, field)` | `PATCH /forms/{form_id}/fields/{field_id}` |
| 6 | `delete_field(form_id, field_id)` | `DELETE /forms/{form_id}/fields/{field_id}` |
| 7 | `publish_form(form_id)` | `POST /forms/{form_id}/publish` |
| 8 | `rename_form(form_id, title)` | `PATCH /forms/{form_id}` |
| 9 | `set_pdf_template(form_id, key)` | `PUT /forms/{form_id}/pdf-template` |
| 10 | `delete_form(form_id)` | `DELETE /forms/{form_id}` |
| 11 | `clone_form(form_id)` | `POST /forms/{form_id}/clone` |
| 12 | `add_logic_rules(form_id, rules)` | `POST /forms/{form_id}/logic-rules` |
| 13 | `edit_logic_rule(form_id, rule_id, rule)` | `PUT /forms/{form_id}/logic-rules/{rule_id}` |
| 14 | `delete_logic_rule(form_id, rule_id)` | `DELETE /forms/{form_id}/logic-rules/{rule_id}` |
| 15 | `list_submissions(form_id, page=1, page_size=25, status=None)` | `GET /forms/{form_id}/submissions` |
| 16 | `get_submission(submission_id)` | `GET /submissions/{submission_id}` |
| 17 | `create_submission(form_id, answers)` | `POST /forms/{form_id}/submissions` |
| 18 | `set_submission_status(submission_id, status)` | `PATCH /submissions/{submission_id}/status` |
| 19 | `delete_submission(submission_id)` | `DELETE /submissions/{submission_id}` |
| 20 | `submission_stats(form_id)` | `GET /forms/{form_id}/stats` |
| 21 | `list_templates(language="es")` | `GET /templates?language=` |
| 22 | `create_form_from_template(template_id)` | `POST /forms/from-template/{template_id}` |
| 23 | `list_webhooks(form_id)` | `GET /forms/{form_id}/webhooks` |
| 24 | `add_webhook(form_id, url)` | `POST /forms/{form_id}/webhooks` |
| 25 | `delete_webhook(form_id, webhook_id)` | `DELETE /forms/{form_id}/webhooks/{webhook_id}` |

`fields`/`field` are plain dicts: `{type, label, required?, options?, rows?, columns?}`.
`rules`/`rule`: `{match: "all"|"any", if: [...], then: [...]}`. `answers` is a dict keyed
by field id, with string or list-of-string values.

## Errors

Non-2xx responses raise `AnotaApiError` with the HTTP status and the server's message:

```python
from anota_api import AnotaApiError

try:
    client.publish_form("does-not-exist")
except AnotaApiError as error:
    print(error.status)   # e.g. 404
    print(error.message)  # server message
```

Note: once a form has been published, its existing fields are locked
(`edit_field`/`delete_field` return 400); you can always `add_fields`.

Network-level failures surface as the standard library's own `urllib.error.URLError`,
not wrapped.

## License

MIT
