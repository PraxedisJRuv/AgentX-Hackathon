import requests
from requests.auth import HTTPBasicAuth
from typing import TypedDict
import os
from dotenv import load_dotenv
import json

load_dotenv()


class IssueData(TypedDict):
    summary: str
    description: str
    title: str
    priority: str


class JiraClient:
    def __init__(self):
        self.base_url = f"https://{os.getenv('JIRA_BASE_URL')}/rest/api/3"
        self.auth = HTTPBasicAuth(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_KEY"))
        self.project_key = "10001"

    def create_issue(self, issue_data: IssueData) -> str:
        """Create a Jira issue and return the new issue key (e.g. 'PROJ-42')."""
        url = f"{self.base_url}/issue"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        payload = json.dumps({
            "fields": {
                "project": {"key": self.project_key},
                "summary": issue_data["title"],
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": issue_data["description"]}],
                        }
                    ],
                },
                "issuetype": {"name": "Bug"},
                "priority": {"name": issue_data["priority"]},
            }
        })

        response = requests.post(url, data=payload, headers=headers, auth=self.auth)
        response.raise_for_status()
        return response.json().get("key")

    def attach_file_to_issue(self, issue_key: str, image_bytes: bytes, filename: str = "image.jpg"):
        """Attach an image (provided as bytes) to an existing Jira issue."""
        url = f"{self.base_url}/issue/{issue_key}/attachments"

        headers = {
            "Accept": "application/json",
            "X-Atlassian-Token": "no-check",
        }

        response = requests.post(
            url,
            headers=headers,
            auth=self.auth,
            files={"file": (filename, image_bytes, "image/jpeg")},
        )
        response.raise_for_status()
        return response.json().get("key")

