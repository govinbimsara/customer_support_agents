"""Unit tests for Jira ticket operations."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.tools.ticket import (
    create_jira_ticket,
    get_user_tickets,
    get_ticket_by_key,
)


class TestCreateJiraTicket:
    """Test cases for create_jira_ticket function."""

    @patch("src.tools.ticket.requests.post")
    def test_create_ticket_success(self, mock_post: Mock) -> None:
        """Test successful ticket creation."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "10001",
            "key": "GEN-23",
            "self": "https://api.atlassian.com/ex/jira/test/rest/api/3/issue/10001",
        }
        mock_post.return_value = mock_response

        result = create_jira_ticket(
            "user123", "Test Issue", "Test description", "Task"
        )

        assert result["status_code"] == 201
        assert result["key"] == "GEN-23"
        assert "error" not in result

    @patch("src.tools.ticket.requests.post")
    def test_create_ticket_failure(self, mock_post: Mock) -> None:
        """Test ticket creation failure."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        result = create_jira_ticket(
            "user123", "Test Issue", "Test description", "Task"
        )

        assert result["status_code"] == 400
        assert result["error"] == "Failed to create ticket"

    @patch("src.tools.ticket.requests.post")
    def test_create_ticket_network_error(self, mock_post: Mock) -> None:
        """Test network error during ticket creation."""
        mock_post.side_effect = Exception("Network error")

        result = create_jira_ticket(
            "user123", "Test Issue", "Test description", "Task"
        )

        assert result["status_code"] == 500
        assert result["error"] == "Network error creating ticket"


class TestGetUserTickets:
    """Test cases for get_user_tickets function."""

    @patch("src.tools.ticket.requests.get")
    def test_get_tickets_success(self, mock_get: Mock) -> None:
        """Test successful retrieval of user tickets."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "issues": [
                {
                    "key": "GEN-23",
                    "fields": {
                        "summary": "Test ticket",
                        "description": {},
                    },
                }
            ]
        }
        mock_get.return_value = mock_response

        result = get_user_tickets("user123")

        assert result["status_code"] == 200
        assert len(result["tickets"]) == 1
        assert result["tickets"][0]["ticket_id"] == "GEN-23"

    @patch("src.tools.ticket.requests.get")
    def test_get_tickets_failure(self, mock_get: Mock) -> None:
        """Test failure retrieving user tickets."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        result = get_user_tickets("user123")

        assert result["status_code"] == 403
        assert result["error"] == "Failed to retrieve tickets"


class TestGetTicketByKey:
    """Test cases for get_ticket_by_key function."""

    @patch("src.tools.ticket.requests.get")
    def test_get_ticket_success(self, mock_get: Mock) -> None:
        """Test successful retrieval of ticket by key."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "issues": [
                {
                    "key": "GEN-23",
                    "fields": {
                        "summary": "Test ticket",
                        "description": {
                            "content": [
                                {
                                    "content": [
                                        {"type": "text", "text": "Test desc"}
                                    ]
                                }
                            ]
                        },
                        "issuetype": {"name": "Task"},
                        "status": {"name": "Open"},
                        "resolution": None,
                    },
                }
            ]
        }
        mock_get.return_value = mock_response

        result = get_ticket_by_key("user123", "GEN-23")

        assert result["status_code"] == 200
        assert result["ticket"]["ticket_id"] == "GEN-23"
        assert result["ticket"]["summary"] == "Test ticket"

    @patch("src.tools.ticket.requests.get")
    def test_get_ticket_not_found(self, mock_get: Mock) -> None:
        """Test ticket not found."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"issues": []}
        mock_get.return_value = mock_response

        result = get_ticket_by_key("user123", "GEN-999")

        assert result["status_code"] == 404
        assert "not found" in result["error"]
