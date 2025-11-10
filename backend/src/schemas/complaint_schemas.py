"""Pydantic schemas for complaint handling."""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class ComplaintOutput(BaseModel):
    """Output schema for ComplaintFlowAgent."""

    ticket_id: str = Field(..., description="Generated ticket ID")
    status: Literal["created", "failed"] = Field(
        ..., description="Ticket creation status"
    )
    issue_type: str = Field(..., description="Type of issue reported")
    original_language: Literal["english", "sinhala", "tamil"] = Field(
        ..., description="Original language of complaint"
    )
    # amazonq-ignore-next-line
    error_message: Optional[str] = Field(
        None, description="Error message if status is failed"
    )


class ComplaintData(BaseModel):
    """Structured complaint data for validation."""

    customer_id: str = Field(..., description="Customer identifier")
    issue_type: str = Field(..., description="Type of issue")
    description: str = Field(..., description="Issue description")
    language: Literal["english", "sinhala", "tamil"] = Field(
        ..., description="Original language for auditing"
    )


class TicketResponse(BaseModel):
    """Response from ticket creation."""

    success: bool = Field(..., description="Whether ticket was created")
    # amazonq-ignore-next-line
    ticket_id: str = Field(..., description="Generated ticket ID")
    ticket_url: str = Field(..., description="URL to view ticket")
    timestamp: str = Field(..., description="Creation timestamp")
    message: str = Field(..., description="Status message")
