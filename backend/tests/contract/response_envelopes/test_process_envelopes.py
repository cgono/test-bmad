import asyncio
from collections.abc import Mapping
from unittest.mock import AsyncMock, patch

from app.adapters.ocr_provider import RawOcrSegment
from app.api.v1.process import process_image
from app.schemas.process import (
    OcrData,
    OcrSegment,
    ProcessData,
    ProcessError,
    ProcessResponse,
    ProcessWarning,
)

from helpers import PNG_1X1_BYTES, StubOcrProvider, _request_with_body


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
        assert "ocr" in envelope["data"]
        ocr = envelope["data"]["ocr"]
        assert isinstance(ocr, Mapping)
        assert isinstance(ocr["segments"], list)
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
        assert "category" in envelope["error"]
        assert "data" not in envelope


def test_process_endpoint_success_envelope_contract() -> None:
    with patch(
        "app.services.ocr_service.get_ocr_provider",
        return_value=StubOcrProvider([RawOcrSegment(text="你好", language="zh", confidence=0.91)]),
    ):
        response = asyncio.run(process_image(_request_with_body(PNG_1X1_BYTES, "image/png")))
    assert_process_envelope(response.model_dump(exclude_none=True))


def test_process_endpoint_partial_envelope_contract() -> None:
    partial_response = ProcessResponse(
        status="partial",
        request_id="req-partial-contract",
        data=ProcessData(
            ocr=OcrData(segments=[OcrSegment(text="你好", language="zh", confidence=0.5)]),
            message="partially-processed",
        ),
        warnings=[ProcessWarning(code="ocr-low-confidence", message="Low confidence score")],
    )
    with patch(
        "app.api.v1.process._build_process_response",
        new=AsyncMock(return_value=partial_response),
    ):
        response = asyncio.run(process_image(_request_with_body(PNG_1X1_BYTES, "image/png")))
    assert_process_envelope(response.model_dump(exclude_none=True))


def test_process_endpoint_error_envelope_contract() -> None:
    error_response = ProcessResponse(
        status="error",
        request_id="req-error-contract",
        error=ProcessError(
            category="validation",
            code="invalid-image",
            message="Image could not be processed",
        ),
    )
    with patch(
        "app.api.v1.process._build_process_response",
        new=AsyncMock(return_value=error_response),
    ):
        response = asyncio.run(process_image(_request_with_body(PNG_1X1_BYTES, "image/png")))
    assert_process_envelope(response.model_dump(exclude_none=True))


def test_process_endpoint_validation_error_contract() -> None:
    response = asyncio.run(process_image(_request_with_body(b"nope", "image/png")))
    payload = response.model_dump(exclude_none=True)
    assert payload["status"] == "error"
    assert payload["error"]["category"] == "validation"
    assert payload["error"]["code"] == "image_decode_failed"
    assert "requestId" not in payload
    assert "payload" not in payload
