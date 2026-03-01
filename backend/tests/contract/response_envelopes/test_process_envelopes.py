from collections.abc import Mapping
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.process import ProcessData, ProcessError, ProcessResponse, ProcessWarning


client = TestClient(app)


def assert_process_envelope(envelope: Mapping[str, object]) -> None:
    assert "status" in envelope
    assert envelope["status"] in {"success", "partial", "error"}

    assert "request_id" in envelope
    assert isinstance(envelope["request_id"], str)
    assert envelope["request_id"]

    # Contract is strict snake_case with stable top-level keys.
    assert "requestId" not in envelope
    assert "payload" not in envelope

    status = envelope["status"]
    if status == "success":
        assert "data" in envelope
        assert isinstance(envelope["data"], Mapping)
        assert "warnings" not in envelope
        assert "error" not in envelope
    elif status == "partial":
        assert "data" in envelope
        assert isinstance(envelope["data"], Mapping)
        assert "warnings" in envelope
        assert isinstance(envelope["warnings"], list)
        assert "error" not in envelope
    else:
        assert "error" in envelope
        assert isinstance(envelope["error"], Mapping)
        assert "data" not in envelope


def test_process_endpoint_success_envelope_contract() -> None:
    """Live endpoint test: success envelope from /v1/process."""
    response = client.post("/v1/process")
    assert response.status_code == 200
    assert_process_envelope(response.json())


def test_process_endpoint_partial_envelope_contract() -> None:
    """Live endpoint test: partial envelope shape from /v1/process (future OCR partial result)."""
    partial_response = ProcessResponse(
        status="partial",
        request_id="req-partial-contract",
        data=ProcessData(message="partially-processed"),
        warnings=[ProcessWarning(code="ocr-low-confidence", message="Low confidence score")],
    )
    with patch(
        "app.api.v1.process._build_process_response",
        new=AsyncMock(return_value=partial_response),
    ):
        response = client.post("/v1/process")
    assert response.status_code == 200
    assert_process_envelope(response.json())


def test_process_endpoint_error_envelope_contract() -> None:
    """Live endpoint test: error envelope shape from /v1/process (future OCR failure)."""
    error_response = ProcessResponse(
        status="error",
        request_id="req-error-contract",
        error=ProcessError(code="invalid-image", message="Image could not be processed"),
    )
    with patch(
        "app.api.v1.process._build_process_response",
        new=AsyncMock(return_value=error_response),
    ):
        response = client.post("/v1/process")
    assert response.status_code == 200
    assert_process_envelope(response.json())
