"""Official Python client for the anota API (https://anota.cloud).

A thin, dependency-free client over the 25-operation anota REST API. Responses
are returned as parsed JSON (dicts/lists); this client does not impose rigid
response model classes.
"""

import json
import urllib.error
import urllib.parse
import urllib.request

__all__ = ["AnotaClient", "AnotaApiError"]
__version__ = "1.0.0"

DEFAULT_BASE_URL = "https://anota.cloud/api/v1"


class AnotaApiError(Exception):
    """Raised for any non-2xx response from the anota API.

    Attributes:
        status: the HTTP status code.
        message: the server's message (from problem-details ``detail``, then
            ``title``, then the raw body).
    """

    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


class AnotaClient:
    def __init__(self, api_key, base_url=DEFAULT_BASE_URL):
        if not api_key:
            raise ValueError(
                "api_key is required (create one at https://anota.cloud/api-keys)"
            )
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _request(self, method, path, body=None, query=None):
        url = self.base_url + path
        if query:
            pairs = [(k, v) for k, v in query.items() if v is not None]
            if pairs:
                url += "?" + urllib.parse.urlencode(pairs)

        data = None
        headers = {"Authorization": "Bearer " + self.api_key}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request) as response:
                text = response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            raw = error.read().decode("utf-8", "replace")
            message = raw
            try:
                problem = json.loads(raw)
                message = problem.get("detail") or problem.get("title") or raw
            except (ValueError, AttributeError):
                pass
            raise AnotaApiError(error.code, message) from None

        return json.loads(text) if text else None

    # ----- forms -----
    def list_forms(self):
        return self._request("GET", "/forms")

    def create_form(self, title, fields, description=None):
        return self._request(
            "POST", "/forms", {"title": title, "fields": fields, "description": description}
        )

    def get_form(self, form_id):
        return self._request("GET", "/forms/" + form_id)

    def add_fields(self, form_id, fields):
        return self._request("POST", "/forms/" + form_id + "/fields", {"fields": fields})

    def edit_field(self, form_id, field_id, field):
        return self._request(
            "PATCH",
            "/forms/" + form_id + "/fields/" + urllib.parse.quote(field_id, safe=""),
            {"field": field},
        )

    def delete_field(self, form_id, field_id):
        return self._request(
            "DELETE",
            "/forms/" + form_id + "/fields/" + urllib.parse.quote(field_id, safe=""),
        )

    def publish_form(self, form_id):
        return self._request("POST", "/forms/" + form_id + "/publish")

    def rename_form(self, form_id, title):
        return self._request("PATCH", "/forms/" + form_id, {"title": title})

    def set_pdf_template(self, form_id, key):
        return self._request("PUT", "/forms/" + form_id + "/pdf-template", {"key": key})

    def delete_form(self, form_id):
        return self._request("DELETE", "/forms/" + form_id)

    def clone_form(self, form_id):
        return self._request("POST", "/forms/" + form_id + "/clone")

    # ----- logic rules -----
    def add_logic_rules(self, form_id, rules):
        return self._request(
            "POST", "/forms/" + form_id + "/logic-rules", {"rules": rules}
        )

    def edit_logic_rule(self, form_id, rule_id, rule):
        return self._request(
            "PUT",
            "/forms/" + form_id + "/logic-rules/" + urllib.parse.quote(rule_id, safe=""),
            {"rule": rule},
        )

    def delete_logic_rule(self, form_id, rule_id):
        return self._request(
            "DELETE",
            "/forms/" + form_id + "/logic-rules/" + urllib.parse.quote(rule_id, safe=""),
        )

    # ----- submissions -----
    def list_submissions(self, form_id, page=1, page_size=25, status=None):
        return self._request(
            "GET",
            "/forms/" + form_id + "/submissions",
            None,
            {"page": page, "pageSize": page_size, "status": status},
        )

    def get_submission(self, submission_id):
        return self._request("GET", "/submissions/" + submission_id)

    def create_submission(self, form_id, answers):
        return self._request(
            "POST", "/forms/" + form_id + "/submissions", {"answers": answers}
        )

    def set_submission_status(self, submission_id, status):
        return self._request(
            "PATCH", "/submissions/" + submission_id + "/status", {"status": status}
        )

    def delete_submission(self, submission_id):
        return self._request("DELETE", "/submissions/" + submission_id)

    def submission_stats(self, form_id):
        return self._request("GET", "/forms/" + form_id + "/stats")

    # ----- templates -----
    def list_templates(self, language="es"):
        return self._request("GET", "/templates", None, {"language": language})

    def create_form_from_template(self, template_id):
        return self._request("POST", "/forms/from-template/" + template_id)

    # ----- webhooks -----
    def list_webhooks(self, form_id):
        return self._request("GET", "/forms/" + form_id + "/webhooks")

    def add_webhook(self, form_id, url):
        return self._request("POST", "/forms/" + form_id + "/webhooks", {"url": url})

    def delete_webhook(self, form_id, webhook_id):
        return self._request(
            "DELETE", "/forms/" + form_id + "/webhooks/" + webhook_id
        )
