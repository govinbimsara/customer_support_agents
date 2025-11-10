"""Pydantic schemas for status checking."""

from pydantic import BaseModel, Field


class StatusOutput(BaseModel):
    """Output schema for StatusCheckAgent."""

    ticket_id: str = Field(..., description="Ticket identifier")
    status: str = Field(..., description="Current ticket status")
    last_updated: str = Field(..., description="Last update timestamp")
