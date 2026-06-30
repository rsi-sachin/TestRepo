"""Pydantic contracts for E2 interface operations."""

from typing import Literal

from pydantic import BaseModel, Field


class E2Request(BaseModel):
    transaction_id: str = Field(..., min_length=1)
    message_type: Literal["subscription", "indication", "control"]
    node_id: str = Field(..., min_length=1)
    payload: dict = Field(default_factory=dict)


class E2Response(BaseModel):
    transaction_id: str
    status: Literal["accepted", "rejected"]
    message: str
    errors: list[str] = Field(default_factory=list)
