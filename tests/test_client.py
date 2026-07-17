import io
import json
import os
import sys
import unittest
from unittest import mock
from urllib.error import HTTPError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from anota_api import AnotaApiError, AnotaClient


class FakeResponse(io.BytesIO):
    """Minimal stand-in for the object urlopen returns (a context manager)."""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
        return False


def capture(response_body=b"{}"):
    """Patch urlopen; return (patcher-managed mock, list that records Requests)."""
    calls = []

    def fake_urlopen(request, *args, **kwargs):
        calls.append(request)
        return FakeResponse(response_body)

    return fake_urlopen, calls


class MethodAndAuthTest(unittest.TestCase):
    def test_list_forms_sends_get_with_bearer_header(self):
        fake, calls = capture(b'[{"id":"f_1"}]')
        with mock.patch("urllib.request.urlopen", fake):
            client = AnotaClient(api_key="anota_sk_test")
            client.list_forms()
        req = calls[0]
        self.assertEqual(req.get_method(), "GET")
        self.assertEqual(req.full_url, "https://anota.cloud/api/v1/forms")
        self.assertEqual(req.get_header("Authorization"), "Bearer anota_sk_test")


class JsonBodyTest(unittest.TestCase):
    def test_create_submission_sends_json_body(self):
        fake, calls = capture(b'{"id":"s_1"}')
        with mock.patch("urllib.request.urlopen", fake):
            client = AnotaClient(api_key="anota_sk_test")
            client.create_submission("f_1", {"f_1": "hola"})
        req = calls[0]
        self.assertEqual(req.get_method(), "POST")
        self.assertEqual(req.full_url, "https://anota.cloud/api/v1/forms/f_1/submissions")
        self.assertEqual(json.loads(req.data.decode("utf-8")), {"answers": {"f_1": "hola"}})
        self.assertEqual(req.get_header("Content-type"), "application/json")


class ErrorTest(unittest.TestCase):
    def test_problem_details_detail_raises_anota_api_error(self):
        def raising_urlopen(request, *args, **kwargs):
            raise HTTPError(
                request.full_url,
                400,
                "Bad Request",
                {},
                io.BytesIO(b'{"detail":"Error: bad"}'),
            )

        with mock.patch("urllib.request.urlopen", raising_urlopen):
            client = AnotaClient(api_key="anota_sk_test")
            with self.assertRaises(AnotaApiError) as ctx:
                client.list_forms()
        self.assertEqual(ctx.exception.status, 400)
        self.assertEqual(ctx.exception.message, "Error: bad")
        self.assertEqual(str(ctx.exception), "Error: bad")


class QueryBuildingTest(unittest.TestCase):
    def test_list_submissions_builds_query_and_omits_none_status(self):
        fake, calls = capture(b"{}")
        with mock.patch("urllib.request.urlopen", fake):
            client = AnotaClient(api_key="anota_sk_test")
            client.list_submissions("f_1", 2, 10, "New")
        self.assertEqual(
            calls[0].full_url,
            "https://anota.cloud/api/v1/forms/f_1/submissions?page=2&pageSize=10&status=New",
        )

    def test_list_submissions_omits_status_when_none(self):
        fake, calls = capture(b"{}")
        with mock.patch("urllib.request.urlopen", fake):
            client = AnotaClient(api_key="anota_sk_test")
            client.list_submissions("f_1")
        self.assertEqual(
            calls[0].full_url,
            "https://anota.cloud/api/v1/forms/f_1/submissions?page=1&pageSize=25",
        )


class EmptyBodyTest(unittest.TestCase):
    def test_empty_response_body_returns_none(self):
        fake, calls = capture(b"")
        with mock.patch("urllib.request.urlopen", fake):
            client = AnotaClient(api_key="anota_sk_test")
            result = client.delete_form("f_1")
        self.assertIsNone(result)


class ConstructorTest(unittest.TestCase):
    def test_missing_api_key_raises(self):
        with self.assertRaises(ValueError):
            AnotaClient(api_key="")

    def test_base_url_trailing_slash_trimmed(self):
        fake, calls = capture(b"{}")
        with mock.patch("urllib.request.urlopen", fake):
            client = AnotaClient(api_key="k", base_url="https://example.test/api/v1/")
            client.list_forms()
        self.assertEqual(calls[0].full_url, "https://example.test/api/v1/forms")


class ContractCoverageTest(unittest.TestCase):
    def test_all_25_methods_exist(self):
        expected = [
            "list_forms", "create_form", "get_form", "add_fields", "edit_field",
            "delete_field", "publish_form", "rename_form", "set_pdf_template",
            "delete_form", "clone_form", "add_logic_rules", "edit_logic_rule",
            "delete_logic_rule", "list_submissions", "get_submission",
            "create_submission", "set_submission_status", "delete_submission",
            "submission_stats", "list_templates", "create_form_from_template",
            "list_webhooks", "add_webhook", "delete_webhook",
        ]
        self.assertEqual(len(expected), 25)
        for name in expected:
            self.assertTrue(
                callable(getattr(AnotaClient, name, None)),
                f"missing method: {name}",
            )


if __name__ == "__main__":
    unittest.main()
