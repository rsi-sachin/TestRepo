"""Pydantic contracts for O1 interface operations."""

from typing import Literal

from pydantic import BaseModel, Field


class O1Request(BaseModel):
    transaction_id: str = Field(..., min_length=1)
    operation: Literal["get", "set", "notify"]
    resource: str = Field(..., min_length=1)
    payload: dict = Field(default_factory=dict)


class O1Response(BaseModel):
    transaction_id: str
    status: Literal["accepted", "rejected"]
    message: str
    errors: list[str] = Field(default_factory=list)
