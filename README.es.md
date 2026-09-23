# anota-api-python · Cliente oficial de Python para la API de [anota](https://anota.cloud)

**[Read me in English](README.md)** · [Referencia interactiva de la API](https://anota.cloud/developers) · [Todos los SDK](https://github.com/anotacloud/anota-api)

![CI](https://github.com/anotacloud/anota-api-python/actions/workflows/ci.yml/badge.svg)

Crea y publica formularios, edita campos y lógica condicional, lee y escribe
respuestas, y conecta webhooks — todo lo que la API REST de anota puede hacer, desde Python.

El cliente no tiene dependencias (solo la biblioteca estándar de Python) y es ligero:
las respuestas regresan como diccionarios y listas de Python normales, así que nunca
peleas contra clases de modelo rígidas.

## Instalación

```bash
pip install git+https://github.com/anotacloud/anota-api-python.git
```

O descarga el [ZIP](https://github.com/anotacloud/anota-api-python/archive/refs/heads/main.zip) / [Tarball](https://github.com/anotacloud/anota-api-python/archive/refs/heads/main.tar.gz) y agrega `src/` a tu ruta.

Requiere Python 3.9 o superior.

## Inicio rápido

```python
import os
from anota_api import AnotaClient

client = AnotaClient(api_key=os.environ["ANOTA_API_KEY"])

form = client.create_form(
    title="Contáctanos",
    fields=[{"type": "text", "label": "Nombre", "required": True}],
)
client.publish_form(form["id"])
client.create_submission(form["id"], {"Nombre": "Ada"})

print(client.list_submissions(form["id"]))
```

Hay un script completo y ejecutable en [`examples/end_to_end.py`](examples/end_to_end.py).

## Autenticación

Crea una clave de API en tu workspace en https://anota.cloud/api-keys y pásala al
cliente. Las claves se ven como `anota_sk_…` y también habilitan el conector MCP de Claude.

```python
client = AnotaClient(api_key="anota_sk_…")
# apunta a otro entorno si lo necesitas:
client = AnotaClient(api_key="anota_sk_…", base_url="https://anota.cloud/api/v1")
```

## Todos los métodos

Cada método devuelve la respuesta JSON ya interpretada (un `dict`, una `list` o `None`
para cuerpos vacíos).

| # | Método | HTTP |
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

**El secreto de firma del webhook se muestra una sola vez.** `add_webhook(form_id, url)` devuelve el `secret` completo (`whsec_…`) en su respuesta (`id`, `formId`, `url`, `secret`, `note`): guárdalo en ese momento. `list_webhooks(form_id)` nunca lo devuelve: cada fila trae `secretHint` (`whsec_…` más los últimos 4 caracteres, o solo `whsec_…` si el secreto es corto) y `secretNote` en lugar de `secret`. Si lo pierdes, elimina el webhook y vuelve a agregarlo para obtener un secreto nuevo. Consulta [CHANGELOG.md](CHANGELOG.md).

`fields`/`field` son diccionarios simples: `{type, label, required?, options?, rows?, columns?}`.
`rules`/`rule`: `{match: "all"|"any", if: [...], then: [...]}`. `answers` es un diccionario
con las claves de los campos (field id) y valores de tipo string o lista de strings.

## Errores

Las respuestas que no sean 2xx lanzan `AnotaApiError` con el código de estado HTTP y el
mensaje del servidor:

```python
from anota_api import AnotaApiError

try:
    client.publish_form("no-existe")
except AnotaApiError as error:
    print(error.status)   # p. ej. 404
    print(error.message)  # mensaje del servidor
```

Nota: una vez que un formulario ha sido publicado, sus campos existentes quedan
bloqueados (`edit_field`/`delete_field` devuelven 400); siempre puedes usar `add_fields`.

Los fallos a nivel de red se manifiestan como el propio `urllib.error.URLError` de la
biblioteca estándar, sin envolver.

## Licencia

MIT
