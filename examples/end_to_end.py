"""End-to-end example: create a form, add a field, publish, submit, and list.

Run with your API key in the environment:

    ANOTA_API_KEY=anota_sk_... python examples/end_to_end.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from anota_api import AnotaApiError, AnotaClient


def main():
    api_key = os.environ.get("ANOTA_API_KEY")
    if not api_key:
        raise SystemExit("Set ANOTA_API_KEY (create one at https://anota.cloud/api-keys)")

    client = AnotaClient(api_key=api_key)

    try:
        form = client.create_form(
            title="Contact us",
            fields=[{"type": "text", "label": "Name", "required": True}],
        )
        form_id = form["id"]
        print("created form:", form_id)

        client.add_fields(form_id, [{"type": "email", "label": "Email"}])
        print("added a field")

        client.publish_form(form_id)
        print("published")

        submission = client.create_submission(form_id, {"Name": "Ada", "Email": "ada@example.com"})
        print("created submission:", submission["id"])

        submissions = client.list_submissions(form_id, page=1, page_size=25)
        print("submissions on page 1:", submissions)
    except AnotaApiError as error:
        print(f"API error {error.status}: {error.message}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
