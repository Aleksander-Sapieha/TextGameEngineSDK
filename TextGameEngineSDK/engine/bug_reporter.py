import urllib.request
import urllib.error
import json
import sys

class BugReporter:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_bug_report(self, description):
        data = json.dumps({
            "content": (
                f"**New Bug Report**\n\n"
                f"Python version: {sys.version}\n\n"
                f"Operating System: {sys.platform}\n\n"
                f"{description}"
            )
        }).encode("utf-8")

        req = urllib.request.Request(
            self.webhook_url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "TextGameEngineSDK/1.0"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req) as response:
                print("Bug report sent!")

        except urllib.error.HTTPError as e:
            print("Discord HTTP error:", e.code)
            print(e.read().decode("utf-8"))

        except urllib.error.URLError as e:
            print("Connection error:", e.reason)