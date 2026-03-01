from typing import Literal

from pydantic import BaseModel, ConfigDict


class ProcessPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    message: str
    job_id: str | None = None


class ProcessResponse(BaseModel):
    status: Literal["success", "partial", "error"]
    request_id: str
    payload: ProcessPayload
