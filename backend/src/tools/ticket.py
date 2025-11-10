import base64
import json
import os
from pathlib import Path
from typing import Dict, Union

import requests
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / "agents" / ".env"
load_dotenv(dotenv_path=env_path)

JIRA_PROJECT = os.environ.get("JIRA_PROJECT")
JIRA_CLOUD = os.environ.get("JIRA_CLOUD")
JIRA_TOKEN = os.environ.get("JIRA_TOKEN")
JIRA_EMAIL = os.environ.get("JIRA_EMAIL")


def create_jira_ticket(
    user_id: str, summary: str, description: str, issue_type: str
) -> Dict[str, Union[str, int]]:
    """Creates a Jira issue with a customer data.

    Args:
        user_id: The unique ID of the user (stored in customfield_10088).
        summary: Short title or summary of the issue.
        description: Detailed description of the issue.
        issue_type: Type of issue to create (e.g., 'Settlement', 'On Boarding').

    Returns:
        Dictionary containing:
            - id: The internal Jira issue ID.
            - key: Ticket ID for the customer (e.g., 'GEN-23'), this is for the customer to refer later.
            - self: The REST API URL to the created issue.
            - status_code: The HTTP response code.
            - error: Error message if request failed.
    """
    url = f"https://api.atlassian.com/ex/jira/{JIRA_CLOUD}/rest/api/3/issue"

    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}],
                    }
                ],
            },
            "issuetype": {"name": issue_type},
            "customfield_10088": user_id,
        }
    }

    auth_string = f"{JIRA_EMAIL}:{JIRA_TOKEN}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code not in [200, 201]:
        return {"error": response.text, "status_code": response.status_code}

    return {"status_code": response.status_code, **response.json()}



def get_user_tickets(user_id: str) -> Dict[str, Union[str, int, list]]:
    """Retrieves existing Jira tickets for a specific user.

    Args:
        user_id: The unique ID of the user stored in Jira custom field
                 'customfield_10088'. This identifies which customer's
                 tickets to retrieve.

    Returns:
        Dictionary containing:
            - status_code: HTTP response status code (200 for success).
            - tickets: List of ticket dictionaries, each containing:
                - ticket_id: Jira ticket identifier (e.g., 'GEN-23') used for
                       customer reference and status tracking.
                - summary: Short title or summary of the ticket.
                # - description: Detailed description of the issue in plain text.
                # - issue_type: Type of issue (e.g., 'Settlement', 'On Boarding',
                #              'Task', 'Bug').
                # - status: Current ticket status (e.g., 'Open', 'In Progress',
                #          'Done', 'Closed').
                # - resolution: Resolution status if ticket is resolved
                #              (e.g., 'Fixed', 'Won\'t Fix', 'Duplicate'),
                #              or None if unresolved.
            - error: Error message string if request failed (only present
                    on failure).
    """
    jql = f'project = {JIRA_PROJECT} AND "customfield_10088" ~ "{user_id}"'
    url = f"https://api.atlassian.com/ex/jira/{JIRA_CLOUD}/rest/api/3/search/jql"

    params = {
        "jql": jql,
        "fields": "summary,description,issuetype,status,resolution",
        "maxResults": 100,
    }

    auth_string = f"{JIRA_EMAIL}:{JIRA_TOKEN}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Accept": "application/json",
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return {"error": response.text, "status_code": response.status_code}

    data = response.json()
    tickets = []

    for issue in data.get("issues", []):
        fields = issue.get("fields", {})
        description_content = fields.get("description", {})

        description_text = ""
        if isinstance(description_content, dict):
            for content_block in description_content.get("content", []):
                for item in content_block.get("content", []):
                    if item.get("type") == "text":
                        description_text += item.get("text", "")

        tickets.append(
            {
                "ticket_id": issue.get("key"),
                "summary": fields.get("summary"),
                # "description": description_text,
                # "issue_type": fields.get("issuetype", {}).get("name"),
                # "status": fields.get("status", {}).get("name"),
                # "resolution": fields.get("resolution", {}).get("name") if fields.get("resolution") else None,
            }
        )

    return {"status_code": response.status_code, "tickets": tickets}


def get_ticket_by_key(
    user_id: str, ticket_id: str
) -> Dict[str, Union[str, int, dict]]:
    """Retrieves a single Jira ticket by its key for a specific user.

    Args:
        user_id: The unique ID of the user stored in Jira custom field
                 'customfield_10088'. Used to verify ticket ownership.
        ticket_id: The Jira ticket identifier (e.g., 'GEN-23') to retrieve.

    Returns:
        Dictionary containing:
            - status_code: HTTP response status code (200 for success).
            - ticket: Dictionary containing ticket details:
                - ticket_id: Jira ticket identifier (e.g., 'GEN-23').
                - summary: Short title or summary of the ticket.
                - description: Detailed description of the issue in plain text.
                - issue_type: Type of issue (e.g., 'Settlement', 'On Boarding',
                             'Task', 'Bug').
                - status: Current ticket status (e.g., 'Open', 'In Progress',
                         'Done', 'Closed').
                - resolution: Resolution status if ticket is resolved
                             (e.g., 'Fixed', 'Won\'t Fix', 'Duplicate'),
                             or None if unresolved.
            - error: Error message string if request failed or ticket not
                    found (only present on failure).
    """
    jql = f'key = {ticket_id} AND project = {JIRA_PROJECT} AND "customfield_10088" ~ "{user_id}"'
    url = f"https://api.atlassian.com/ex/jira/{JIRA_CLOUD}/rest/api/3/search/jql"

    params = {
        "jql": jql,
        "fields": "summary,description,issuetype,status,resolution",
        "maxResults": 1,
    }

    auth_string = f"{JIRA_EMAIL}:{JIRA_TOKEN}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Accept": "application/json",
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return {"error": response.text, "status_code": response.status_code}

    data = response.json()
    issues = data.get("issues", [])

    if not issues:
        return {
            "error": f"Ticket {ticket_id} not found for user {user_id}",
            "status_code": 404,
        }

    issue = issues[0]
    fields = issue.get("fields", {})
    description_content = fields.get("description", {})

    description_text = ""
    if isinstance(description_content, dict):
        for content_block in description_content.get("content", []):
            for item in content_block.get("content", []):
                if item.get("type") == "text":
                    description_text += item.get("text", "")

    ticket = {
        "ticket_id": issue.get("key"),
        "summary": fields.get("summary"),
        "description": description_text,
        "issue_type": fields.get("issuetype", {}).get("name"),
        "status": fields.get("status", {}).get("name"),
        "resolution": fields.get("resolution", {}).get("name")
        if fields.get("resolution")
        else None,
    }

    return {"status_code": response.status_code, "ticket": ticket}


if __name__ == "__main__":
    # print(f"JIRA_PROJECT: {JIRA_PROJECT}")
    # print(f"JIRA_CLOUD: {JIRA_CLOUD}")
    # print(f"JIRA_EMAIL: {JIRA_EMAIL}")
    # print(f"JIRA_TOKEN: {'*' * 10 if JIRA_TOKEN else None}")
    # print()
    # response = create_jira_ticket(
    #     "user123", "Test Issue 3", "This is a test issue 3", "Task"
    # )
    # print(response)

    response = get_user_tickets("user")
    print(response)
